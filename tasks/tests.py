from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
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


class TaskFilterTests(TestCase):
    def setUp(self):
        self.me = User.objects.create_user(username='filterMe', password=TEST_PASSWORD)
        self.other = User.objects.create_user(username='filterOther', password=TEST_PASSWORD)
        self.status_new = Status.objects.create(name='новый-фильтр')
        self.status_done = Status.objects.create(name='завершен-фильтр')
        self.label_bug = Label.objects.create(name='баг-фильтр')
        self.label_feature = Label.objects.create(name='фича-фильтр')

        self.task_mine_new_bug = Task.objects.create(
            name='Моя новая задача с багом',
            status=self.status_new,
            author=self.me,
            executor=self.other,
        )
        self.task_mine_new_bug.labels.add(self.label_bug)

        self.task_others_done_feature = Task.objects.create(
            name='Чужая завершенная задача с фичей',
            status=self.status_done,
            author=self.other,
            executor=self.me,
        )
        self.task_others_done_feature.labels.add(self.label_feature)

        self.client.login(username='filterMe', password=TEST_PASSWORD)

    def test_filter_by_status(self):
        response = self.client.get(reverse('tasks_list'), {'status': self.status_done.pk})
        self.assertContains(response, 'Чужая завершенная задача с фичей')
        self.assertNotContains(response, 'Моя новая задача с багом')

    def test_filter_by_executor(self):
        response = self.client.get(reverse('tasks_list'), {'executor': self.other.pk})
        self.assertContains(response, 'Моя новая задача с багом')
        self.assertNotContains(response, 'Чужая завершенная задача с фичей')

    def test_filter_by_label(self):
        response = self.client.get(reverse('tasks_list'), {'labels': self.label_feature.pk})
        self.assertContains(response, 'Чужая завершенная задача с фичей')
        self.assertNotContains(response, 'Моя новая задача с багом')

    def test_filter_self_tasks(self):
        response = self.client.get(reverse('tasks_list'), {'self_tasks': 'on'})
        self.assertContains(response, 'Моя новая задача с багом')
        self.assertNotContains(response, 'Чужая завершенная задача с фичей')

    def test_no_filter_shows_all_tasks(self):
        response = self.client.get(reverse('tasks_list'))
        self.assertContains(response, 'Моя новая задача с багом')
        self.assertContains(response, 'Чужая завершенная задача с фичей')
