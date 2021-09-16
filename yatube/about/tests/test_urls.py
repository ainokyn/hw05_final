from enum import Enum
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='odin')
        cls.Adress = Enum('Adress', {
            '/about/author/': ['about/author.html', HTTPStatus.OK],
            '/about/tech/': ['about/tech.html', HTTPStatus.OK]})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_correct_status_codes_for_any_user(self):
        """URL-адреса работают корректно для любого пользователя"""
        for adress in self.Adress:
            with self.subTest(adress=adress):
                response = self.guest_client.get(
                    adress.name, follow=True)
                self.assertEqual(response.status_code, adress.value[1])

    def test_urls_about_correct_template(self):
        """Проверка правильности шаблонов приложения About."""
        for adress in self.Adress:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress.name)
                self.assertTemplateUsed(response, adress.value[0])
