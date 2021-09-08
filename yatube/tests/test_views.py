from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post

TestCase.maxDiff = None

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test_slug_2',
            description='Тестовое описание_2',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        number_of_posts = 13
        for post_num in range(number_of_posts):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый текст %s' % post_num,
                group=cls.group,
                image=uploaded,
            )

        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            'posts/index.html': reverse('post:index'),
            'posts/group_list.html': reverse('group:group_list',
                                             kwargs={
                                                 'slug': self.group.slug}),
            'posts/profile.html': reverse(
                'post:profile', kwargs={'username': self.user.username}),
            'posts/post_detail.html': reverse(
                'post:post_detail', kwargs={'post_id': self.post.pk}),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
            'users/logged_out.html': reverse('users:logout'),
            'users/signup.html': reverse('users:signup'),
            'users/password_reset_form.html': reverse(
                'users:password_reset_form'),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_uses_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html."""
        response = self.authorized_client.get(reverse('post:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_update_post_uses_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html."""
        response = self.authorized_client.get(
            reverse('post:update_post', kwargs={
                'post_id': self.post.pk
            }))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_first_page_contains_ten_records(self):
        """Проверка, паджинатора главной страницы первые 10 постов."""
        cache.clear()
        response = self.guest_client.get(reverse('post:index'))
        self.assertTrue(len(
            response.context['page_obj']) == settings.NUM_POSTS_ON_PAGE)

    def test_second_page_contains_three_records(self):
        """Проверка, паджинатора главной страницы следующие 3 поста."""
        cache.clear()
        response = self.guest_client.get(reverse('post:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_context_index(self):
        """Проверка контекста главной страницы."""
        cache.clear()
        response = self.guest_client.get(reverse('post:index'))
        post_list = Post.objects.all()[:settings.NUM_POSTS_ON_PAGE]
        self.assertEqual(list(response.context['page_obj']), list(post_list))

    def test_context_group_list(self):
        """Проверка контекста списка постов."""
        response = self.guest_client.get(reverse(
            'group:group_list', kwargs={'slug': self.group.slug}))
        post_list = Post.objects.filter(
            group=self.group)[:settings.NUM_POSTS_ON_PAGE]
        self.assertEqual(list(response.context['page_obj']), list(post_list),)

    def test_context_profile(self):
        """Проверка контекста профиля."""
        response = self.guest_client.get(
            reverse('post:profile', kwargs={'username': self.user}))
        post_list = Post.objects.filter(
            author=self.user)[:settings.NUM_POSTS_ON_PAGE]
        self.assertEqual(list(response.context['page_obj']), list(post_list),)

    def test_paginator_group_list_first_ten_obj(self):
        """Проверка, паджинатора страницы со списком
        постов первые 10 постов.
        """
        cache.clear()
        response = self.guest_client.get(
            reverse('group:group_list', kwargs={'slug': self.group.slug}))
        self.assertTrue(len(
            response.context['page_obj']) == settings.NUM_POSTS_ON_PAGE)

    def test_paginator_group_list_last_three_obj(self):
        """Проверка, паджинатора страницы со списком
        постов следующие 3 поста.
        """
        cache.clear()
        response = self.client.get(reverse(
            'group:group_list', kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_paginator_profile_first_ten_obj(self):
        """Проверка, паджинатора профиля первые 10 постов."""
        response = self.guest_client.get(
            reverse('post:profile', kwargs={'username': self.user.username}))
        self.assertTrue(len(
            response.context['page_obj']) == settings.NUM_POSTS_ON_PAGE)

    def test_paginator_profile_last_three_obj(self):
        """Проверка, паджинатора профиля следующие 3 поста."""
        response = self.client.get(reverse('post:profile',
                                   kwargs={
                                       'username': self.user.username
                                   }) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_context_post_detail(self):
        """Проверка контекста страницы поста."""
        response = self.guest_client.get(reverse(
            'post:post_detail', kwargs={'post_id': self.post.pk}))
        post_list = Post.objects.filter(id=1)
        self.assertTrue(response.context['post'], post_list)

    def test_context_post_edit(self):
        """Проверка контекста редактирования страницы поста."""
        response = self.authorized_client.get(
            reverse('post:update_post', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_post_create(self):
        """Проверка контекста создания страницы поста."""
        response = self.authorized_client.get(reverse('post:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_wiht_group_create(self):
        """Проверьте, что если при создании поста указать
        группу, то этот пост появляется на главной.
        """
        self.post_2 = Post.objects.create(
            author=self.user,
            text='Тестовый текст_2',
            group=self.group_2,
        )
        response = self.authorized_client.post(
            reverse('post:index'))
        first_object = response.context['page_obj'][0]
        group_0 = first_object.group
        self.assertEqual(group_0, self.group_2)

    def test_post_wiht_group_group_list(self):
        """Проверьте, что если при создании поста указать
        группу, то этот пост появляется на странице выбранной группы.
        """
        self.post_2 = Post.objects.create(
            author=self.user,
            text='Тестовый текст_2',
            group=self.group_2,
        )
        response = self.authorized_client.post(
            reverse('group:group_list', kwargs={'slug': self.group_2.slug}))
        first_object = response.context['page_obj'][0]
        group_0 = first_object.group
        self.assertEqual(group_0, self.group_2)

    def test_post_wiht_group_profile(self):
        """Проверьте, что если при создании поста указать
        группу, то этот пост появляется в профиле.
        """
        self.post_2 = Post.objects.create(
            author=self.user,
            text='Тестовый текст_2',
            group=self.group_2,
        )
        response = self.authorized_client.post(
            reverse('group:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        group_0 = first_object.group
        self.assertEqual(group_0, self.group_2)

    def test_post_has_corresponding_group(self):
        """Проверьте, что у созданного поста нужная группа."""
        self.assertNotEqual(self.group, self.group_2)

    def test_context_user_form(self):
        """Проверка, что в контексте передаётся форма для
        создания нового пользователя.
        """
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'password1': forms.CharField,
            'password2': forms.CharField,
            'email': forms.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_wiht_comment_post_detail(self):
        """Проверьте, что после успешной отправки комментария он
        появляется на странице поста.
        """
        self.comment = Comment.objects.create(
            author=self.user,
            text='это текст комментария',
            post=self.post,
        )
        response = self.authorized_client.post(
            reverse('group:post_detail', kwargs={'post_id': self.post.pk}))
        first_object = response.context['comments'][0]
        comment_0 = first_object.text
        self.assertEqual(comment_0, 'это текст комментария')

    def test_follow(self):
        """Проверьте, что новая запись пользователя появляется в ленте тех,
        кто на него подписан.
        """
        self.user = User.objects.create(username='author')
        self.user_2 = User.objects.create(username='user')
        Follow.objects.create(user=self.user_2, author=self.user)
        post_list = Post.objects.filter(
            author=self.user, text='hello')[:settings.NUM_POSTS_ON_PAGE]
        response = self.authorized_client.get(reverse(
            'post:follow_index'))
        self.assertEqual(list(response.context['page_obj']), list(post_list))

    def test_unfollow(self):
        """Проверьте, что новая запись пользователя не появляется в ленте тех,
        кто на него не подписан.
        """
        self.user = User.objects.create(username='author')
        self.user_2 = User.objects.create(username='user')
        self.user_3 = User.objects.create(username='new_author')
        Follow.objects.create(user=self.user_2, author=self.user)
        Post.objects.create(author=self.user_3, text='hello_world')
        post_list = list(Post.objects.filter(author=self.user_3,
                                             text='hello_world'))
        response = self.authorized_client.get(reverse(
            'post:follow_index'))
        self.assertNotEqual(list(response.context['page_obj']), post_list)
