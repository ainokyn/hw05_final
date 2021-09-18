from enum import Enum
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user_2 = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.Adress_guest = Enum('Adress_guest', {
                                '/': ['posts/index.html', HTTPStatus.OK],
                                f'/group/{cls.group.slug}/':
                                ['posts/group_list.html', HTTPStatus.OK],
                                f'/profile/{cls.user.username}/':
                                ['posts/profile.html', HTTPStatus.OK],
                                f'/posts/{cls.post.pk}/':
                                ['posts/post_detail.html', HTTPStatus.OK]})

        cls.Adress_authorized = Enum('Adress_authorized', {
            f'/posts/{cls.post.pk}/edit/':
            ['posts/create_post.html', HTTPStatus.OK],
            '/create/': ['posts/create_post.html', HTTPStatus.OK],
            f'/posts/{cls.post.pk}/comment':
            ['no_template', HTTPStatus.OK],
            f'/profile/{cls.user_2.username}/follow/':
            ['no_template', HTTPStatus.OK],
            f'/profile/{cls.user_2.username}/unfollow/':
            ['no_template', HTTPStatus.OK]})

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

    def test_urls_correct_status_codes_for_any_user(self):
        """URL-адрес работает корректно для неизвестной страницы"""
        response = self.guest_client.get('/unexisting/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_correct_status_codes_for_authorized_client(self):
        """URL-адреса работают корректно для авторизированного пользователя"""
        for adress_authorized in self.Adress_authorized:
            with self.subTest(adress_authorized=adress_authorized):
                response = self.authorized_client.get(
                    adress_authorized.name, follow=True)
                self.assertEqual(
                    response.status_code, adress_authorized.value[1])

    def test_urls_post_correct_template_for_guest(self):
        """Проверка правильности шаблонов приложения Post для гостя."""
        cache.clear()
        for adress_guest in self.Adress_guest:
            with self.subTest(adress_guest=adress_guest):
                response = self.guest_client.get(adress_guest.name)
                self.assertTemplateUsed(response, adress_guest.value[0])

    def test_urls_post_correct_template_for_authorized(self):
        """Проверка правильности шаблонов приложения Post для
        авторизированного.
        """
        for adress_authorized in self.Adress_authorized:
            if (adress_authorized.name == f'/posts/{self.post.pk}/edit/'
                                          and '/create/'):
                with self.subTest(adress_authorized=adress_authorized):
                    response = self.authorized_client.get(
                        adress_authorized.name)
                    self.assertTemplateUsed(
                        response, adress_authorized.value[0])

    def test_urls_404_correct_template(self):
        """Проверка правильности шаблона ошибки 404."""
        response = self.authorized_client.get('/unexisting/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_redirect_guestuser_create_post(self):
        """Проверка редиректа неавторизованного пользователя при
        редактировани поста.
        """
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.pk}/edit/')

    def test_status_guestuser_create_post(self):
        """Проверка статуса ответа сервера при запросе неавторизованного
        пользователя на редактировани поста.
        """
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_authorized_user_not_author_create_post(self):
        """Проверка редиректа пользователя при редактировани чужого поста."""
        self.user_1 = User.objects.create(username='user_1')
        self.authorized_client.force_login(self.user_1)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, reverse('post:post_detail',
                             kwargs={'post_id': self.post.pk}))

    def test_status_authorized_user_not_author_create_post(self):
        """Проверка статуса ответа сервера при запросе пользователя
        на редактирование чужого поста.
        """
        self.user_1 = User.objects.create(username='user_1')
        self.authorized_client.force_login(self.user_1)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_status_code_when_authorized_user_unfollow(self):
        """Проверка статуса ответа сервера при отписке."""
        author = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=author)
        response = self.authorized_client.get(
            f'/profile/{author.username}/unfollow/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_code_when_authorized_user_unfollow(self):
        """Проверка редиректа при отписке."""
        author = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=author)
        response = self.authorized_client.get(
            f'/profile/{author.username}/unfollow/')
        self.assertRedirects(response, reverse('post:follow_index'))

    def test_redirect_code_when_authorized_user_follow(self):
        """Проверка редиректа при подписке."""
        author = User.objects.create(username='author_1')
        response = self.authorized_client.get(
            f'/profile/{author.username}/follow/')
        self.assertRedirects(response, reverse('post:follow_index'))
