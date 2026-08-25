from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
from statuses.models import Status
from tasks.models import Task

TEST_PASSWORD = 'BestPassword123'


class LabelAuthGuardTests(TestCase):
    def test_list_requires_login(self):
        response = self.client.get(reverse('labels_list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('labels_list')}")

    def test_create_page_requires_login(self):
        response = self.client.get(reverse('labels_create'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('labels_create')}")


class LabelCrudTests(TestCase):
    fixtures = ['labels.json']

    def setUp(self):
        self.user = User.objects.create_user(username='labelUser', password=TEST_PASSWORD)
        self.client.login(username='labelUser', password=TEST_PASSWORD)

    def test_label_list_shows_fixtures(self):
        response = self.client.get(reverse('labels_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'баг')
        self.assertContains(response, 'фича')

    def test_create_label_success(self):
        response = self.client.post(reverse('labels_create'), {'name': 'вопрос'})
        self.assertRedirects(response, reverse('labels_list'))
        self.assertTrue(Label.objects.filter(name='вопрос').exists())

    def test_create_label_duplicate_name(self):
        response = self.client.post(reverse('labels_create'), {'name': 'баг'})
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('already exists', ' '.join(form.errors.get('name', [])))

    def test_update_label_success(self):
        response = self.client.post(reverse('labels_update', args=[401]), {'name': 'критический баг'})
        self.assertRedirects(response, reverse('labels_list'))
        self.assertEqual(Label.objects.get(pk=401).name, 'критический баг')

    def test_delete_label_success(self):
        response = self.client.post(reverse('labels_delete', args=[401]))
        self.assertRedirects(response, reverse('labels_list'))
        self.assertFalse(Label.objects.filter(pk=401).exists())

    def test_cannot_delete_label_linked_to_task(self):
        status = Status.objects.create(name='новый-для-метки')
        task = Task.objects.create(name='Задача с меткой', status=status, author=self.user)
        task.labels.add(Label.objects.get(pk=401))

        response = self.client.post(reverse('labels_delete', args=[401]))

        self.assertRedirects(response, reverse('labels_list'))
        self.assertTrue(Label.objects.filter(pk=401).exists())
