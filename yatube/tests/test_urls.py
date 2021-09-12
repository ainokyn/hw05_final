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
        cls.adress_guest = ['/', '/about/author/', '/about/tech/',
                            f'/group/{cls.group.slug}/',
                            f'/profile/{cls.user.username}/',
                            f'/posts/{cls.post.pk}/', '/auth/signup/',
                            '/auth/login/']
        cls.code_status_ok = HTTPStatus.OK
        cls.adress_authorized = [f'/posts/{cls.post.pk}/edit/', '/create/',
                                 '/auth/logout/', '/auth/password_reset/',
                                 '/auth/password_change/',
                                 '/auth/password_change/done/',
                                 '/auth/password_reset/done/',
                                 f'/posts/{cls.post.pk}/comment',
                                 f'/profile/{cls.user.username}/follow/',
                                 f'/profile/{cls.user.username}/unfollow/']

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_correct_status_codes_for_any_user(self):
        """URL-адреса работают корректно для любого пользователя"""
        for item in self.adress_guest:
            with self.subTest(item=item):
                response = self.guest_client.get(item, follow=True)
                self.assertEqual(response.status_code, self.code_status_ok)

    def test_urls_correct_status_codes_for_any_user(self):
        """URL-адрес работает корректно для неизвестной страницы"""
        response = self.guest_client.get('/unexisting/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_correct_status_codes_for_authorized_client(self):
        """URL-адреса работают корректно для авторизированного пользователя"""
        for item in self.adress_authorized:
            with self.subTest(item=item):
                response = self.authorized_client.get(item, follow=True)
                self.assertEqual(response.status_code, self.code_status_ok)

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

    def test_redirect_guestuser_create_post(self):
        """Проверка редиректа неавторизованного пользователя при
        редактировани поста.
        """
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_authorized_user_njt_author_create_post(self):
        """Проверка редиректа пользователя при редактировани чужого поста."""
        self.user_1 = User.objects.create(username='user_1')
        self.authorized_client.force_login(self.user_1)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
