from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status

TEST_PASSWORD = 'BestPassword123'


class StatusAuthGuardTests(TestCase):
    def test_list_requires_login(self):
        response = self.client.get(reverse('statuses_list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('statuses_list')}")

    def test_create_page_requires_login(self):
        response = self.client.get(reverse('statuses_create'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('statuses_create')}")


class StatusCrudTests(TestCase):
    fixtures = ['statuses.json']

    def setUp(self):
        self.user = User.objects.create_user(username='statusUser', password=TEST_PASSWORD)
        self.client.login(username='statusUser', password=TEST_PASSWORD)

    def test_status_list_shows_fixtures(self):
        response = self.client.get(reverse('statuses_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'новый')
        self.assertContains(response, 'в работе')

    def test_create_status_success(self):
        response = self.client.post(reverse('statuses_create'), {'name': 'на тестировании'})
        self.assertRedirects(response, reverse('statuses_list'))
        self.assertTrue(Status.objects.filter(name='на тестировании').exists())

    def test_create_status_duplicate_name(self):
        response = self.client.post(reverse('statuses_create'), {'name': 'новый'})
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('already exists', ' '.join(form.errors.get('name', [])))

    def test_update_status_success(self):
        response = self.client.post(reverse('statuses_update', args=[1]), {'name': 'завершен'})
        self.assertRedirects(response, reverse('statuses_list'))
        self.assertEqual(Status.objects.get(pk=1).name, 'завершен')

    def test_delete_status_success(self):
        response = self.client.post(reverse('statuses_delete', args=[1]))
        self.assertRedirects(response, reverse('statuses_list'))
        self.assertFalse(Status.objects.filter(pk=1).exists())
