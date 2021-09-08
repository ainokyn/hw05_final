from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='kok')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_correct_status_codes_for_any_user(self):
        """URL-адреса работают корректно для любого пользователя"""
        urls_status_codes = {
            '/': HTTPStatus.OK.value,
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value,
            f'/group/{self.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{self.user.username}/': HTTPStatus.OK.value,
            f'/posts/{self.post.pk}/': HTTPStatus.OK.value,
            '/unexisting/': HTTPStatus.NOT_FOUND.value,
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
        }
        for adress, code in urls_status_codes.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, code)

    def test_urls_correct_status_codes_for_authorized_client(self):
        """URL-адреса работают корректно для авторизированного пользователя"""
        urls_status_codes = {
            f'/posts/{self.post.pk}/edit/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_change/': HTTPStatus.OK.value,
            '/auth/password_change/done/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            f'/posts/{self.post.pk}/comment': HTTPStatus.OK.value,
            f'/profile/{self.user.username}/follow/': HTTPStatus.OK.value,
            f'/profile/{self.user.username}/unfollow/': HTTPStatus.OK.value,

        }
        for adress, code in urls_status_codes.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress, follow=True)
                self.assertEqual(response.status_code, code)

    def test_urls_post_correct_template(self):
        """Проверка правильности шаблонов приложения Post."""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_about_correct_template(self):
        """Проверка правильности шаблонов приложения About."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_users_correct_template(self):
        """Проверка правильности шаблонов приложения Users."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_404_correct_template(self):
        """Проверка правильности шаблона ошибки 404."""
        response = self.authorized_client.get('/unexisting/')
        self.assertTemplateUsed(response, 'core/404.html')
