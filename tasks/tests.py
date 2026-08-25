from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status
from tasks.models import Task

TEST_PASSWORD = 'BestPassword123'


class TaskAuthGuardTests(TestCase):
    def test_list_requires_login(self):
        response = self.client.get(reverse('tasks_list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tasks_list')}")

    def test_create_page_requires_login(self):
        response = self.client.get(reverse('tasks_create'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tasks_create')}")


class TaskCrudTests(TestCase):
    fixtures = ['tasks.json']

    def setUp(self):
        self.author = User.objects.get(pk=101)
        self.other_user = User.objects.get(pk=102)
        self.status = Status.objects.get(pk=201)
        self.task = Task.objects.get(pk=301)
        self.client.login(username='taskAuthor', password=TEST_PASSWORD)

    def test_task_list_shows_fixture_task(self):
        response = self.client.get(reverse('tasks_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')

    def test_task_detail_shows_fields(self):
        response = self.client.get(reverse('tasks_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
        self.assertContains(response, 'Описание тестовой задачи')

    def test_create_task_sets_author_automatically(self):
        response = self.client.post(reverse('tasks_create'), {
            'name': 'Новая задача',
            'description': 'Описание',
            'status': self.status.pk,
            'executor': '',
            'labels': [],
        })
        self.assertRedirects(response, reverse('tasks_list'))
        task = Task.objects.get(name='Новая задача')
        self.assertEqual(task.author, self.author)

    def test_create_task_duplicate_name(self):
        response = self.client.post(reverse('tasks_create'), {
            'name': 'Тестовая задача',
            'description': 'Описание',
            'status': self.status.pk,
            'executor': '',
            'labels': [],
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('already exists', ' '.join(form.errors.get('name', [])))

    def test_update_task_success(self):
        response = self.client.post(reverse('tasks_update', args=[self.task.pk]), {
            'name': 'Обновленная задача',
            'description': self.task.description,
            'status': self.status.pk,
            'executor': '',
            'labels': [],
        })
        self.assertRedirects(response, reverse('tasks_list'))
        self.assertEqual(Task.objects.get(pk=self.task.pk).name, 'Обновленная задача')

    def test_only_author_can_delete_task(self):
        self.client.logout()
        self.client.login(username='otherUser', password=TEST_PASSWORD)
        response = self.client.post(reverse('tasks_delete', args=[self.task.pk]))
        self.assertRedirects(response, reverse('tasks_list'))
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_author_can_delete_task(self):
        response = self.client.post(reverse('tasks_delete', args=[self.task.pk]))
        self.assertRedirects(response, reverse('tasks_list'))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())


class TaskStatusProtectionTests(TestCase):
    fixtures = ['tasks.json']

    def test_status_used_by_task_cannot_be_deleted(self):
        self.client.login(username='taskAuthor', password=TEST_PASSWORD)
        status = Status.objects.get(pk=201)
        response = self.client.post(reverse('statuses_delete', args=[status.pk]))
        self.assertRedirects(response, reverse('statuses_list'))
        self.assertTrue(Status.objects.filter(pk=status.pk).exists())


class UserTaskProtectionTests(TestCase):
    fixtures = ['tasks.json']

    def test_author_linked_to_task_cannot_be_deleted(self):
        self.client.login(username='taskAuthor', password=TEST_PASSWORD)
        response = self.client.post(reverse('users_delete', args=[101]))
        self.assertRedirects(response, reverse('users_list'))
        self.assertTrue(User.objects.filter(pk=101).exists())
