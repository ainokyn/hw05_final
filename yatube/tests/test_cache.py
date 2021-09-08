from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

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

    def test_cache(self):
        response = self.client.get(reverse('post:index'))
        content_page = response.content
        self.post.delete()
        response_2 = self.client.get(reverse('post:index'))
        content_page_2 = response_2.content
        self.assertEqual(len(content_page_2), len(content_page))
        cache.clear()
        response_3 = self.client.get(reverse('post:index'))
        content_page_3 = response_3.content
        self.assertNotEqual(len(content_page_3), len(content_page))
