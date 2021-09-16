from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup(self):
        """Проверяем, что создаётся новый пользователь."""
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user_count = User.objects.count()
        user_data = {
            'first_name': 'masha',
            'last_name': 'ivanova',
            'username': 'zero',
            'email': 'jhjh@yandex.ru',
            'password1': '123qwe!E!E',
            'password2': '123qwe!E!E',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=user_data,
            follow=True)
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                username=self.user.username,
            ).exists()
        )
