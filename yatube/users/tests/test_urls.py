from enum import Enum
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tor')
        cls.Adress_guest = Enum('Adress_guest', {
                                '/auth/signup/':
                                ['users/signup.html', HTTPStatus.OK],
                                '/auth/login/':
                                ['users/login.html', HTTPStatus.OK],
                                '/auth/password_reset/':
                                ['users/password_reset_form.html',
                                 HTTPStatus.OK],
                                '/auth/password_reset/done/':
                                ['users/password_reset_done.html',
                                 HTTPStatus.OK]})

        cls.Adress_authorized = Enum('Adress_authorized', {
            '/auth/logout/':
            ['users/logged_out.html', HTTPStatus.OK],
            '/auth/password_change/':
            ['users/login.html', HTTPStatus.OK],
            '/auth/password_change/done/':
            ['users/login.html', HTTPStatus.OK]})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_correct_status_codes_for_any_user(self):
        """URL-адреса работают корректно для любого пользователя"""
        for adress_guest in self.Adress_guest:
            with self.subTest(adress_guest=adress_guest):
                response = self.guest_client.get(
                    adress_guest.name, follow=True)
                self.assertEqual(response.status_code, adress_guest.value[1])

    def test_urls_correct_status_codes_for_authorized_client(self):
        """URL-адреса работают корректно для авторизированного пользователя"""
        for adress_authorized in self.Adress_authorized:
            with self.subTest(adress_authorized=adress_authorized):
                response = self.authorized_client.get(
                    adress_authorized.name, follow=True)
                self.assertEqual(
                    response.status_code, adress_authorized.value[1])

    def test_urls_users_correct_template_for_guest(self):
        """Проверка правильности шаблонов приложения Users для гостя."""
        for adress_guest in self.Adress_guest:
            with self.subTest(adress_guest=adress_guest):
                response = self.guest_client.get(adress_guest.name)
                self.assertTemplateUsed(response, adress_guest.value[0])

    def test_urls_users_correct_template_for_authorized(self):
        """Проверка правильности шаблонов приложения User для
        авторизированного.
        """
        for adress_authorized in self.Adress_authorized:
            with self.subTest(adress_authorized=adress_authorized):
                response = self.authorized_client.get(
                    adress_authorized.name,
                    {'username': self.user.username}, follow=True)
                self.assertTemplateUsed(
                    response, adress_authorized.value[0])
