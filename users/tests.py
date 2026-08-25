from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

TEST_PASSWORD = 'BestPassword123'


class UserCreateTests(TestCase):
    def test_create_user_page_loads(self):
        response = self.client.get(reverse('users_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_user_success(self):
        response = self.client.post(reverse('users_create'), {
            'first_name': 'Мария',
            'last_name': 'Смирнова',
            'username': 'newUser',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newUser').exists())

    def test_create_user_duplicate_username(self):
        User.objects.create_user(username='existingUser', password=TEST_PASSWORD)
        response = self.client.post(reverse('users_create'), {
            'first_name': 'Мария',
            'last_name': 'Смирнова',
            'username': 'existingUser',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('already exists', ' '.join(form.errors.get('username', [])))


class UserUpdateTests(TestCase):
    fixtures = ['users.json']

    def test_update_requires_login(self):
        response = self.client.get(reverse('users_update', args=[1]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('users_update', args=[1])}")

    def test_owner_can_update_self(self):
        self.client.login(username='testUser1', password=TEST_PASSWORD)
        response = self.client.post(reverse('users_update', args=[1]), {
            'first_name': 'Иван',
            'last_name': 'Иванов-Обновлённый',
            'username': 'testUser1',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse('users_list'))
        self.assertEqual(User.objects.get(pk=1).last_name, 'Иванов-Обновлённый')

    def test_user_cannot_update_another_user(self):
        self.client.login(username='testUser1', password=TEST_PASSWORD)
        response = self.client.post(reverse('users_update', args=[2]), {
            'first_name': 'Пётр',
            'last_name': 'Взломанный',
            'username': 'testUser2',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse('users_list'))
        self.assertEqual(User.objects.get(pk=2).last_name, 'Петров')


class UserDeleteTests(TestCase):
    fixtures = ['users.json']

    def test_owner_can_delete_self(self):
        self.client.login(username='testUser1', password=TEST_PASSWORD)
        response = self.client.post(reverse('users_delete', args=[1]))
        self.assertRedirects(response, reverse('users_list'))
        self.assertFalse(User.objects.filter(pk=1).exists())

    def test_user_cannot_delete_another_user(self):
        self.client.login(username='testUser1', password=TEST_PASSWORD)
        response = self.client.post(reverse('users_delete', args=[2]))
        self.assertRedirects(response, reverse('users_list'))
        self.assertTrue(User.objects.filter(pk=2).exists())


class UserAuthTests(TestCase):
    fixtures = ['users.json']

    def test_login_success_redirects_to_index(self):
        response = self.client.post(reverse('login'), {
            'username': 'testUser1',
            'password': TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse('index'))

    def test_logout(self):
        self.client.login(username='testUser1', password=TEST_PASSWORD)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('index'))


class UsersListTests(TestCase):
    fixtures = ['users.json']

    def test_users_list_available_without_login(self):
        response = self.client.get(reverse('users_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testUser1')
        self.assertContains(response, 'testUser2')
