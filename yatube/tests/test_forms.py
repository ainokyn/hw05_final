
import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_img(self):
        """Валидная форма создает запись с картинкой в Post."""
        post_count = Post.objects.count()
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
            content_type='image/gif')

        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('post:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post:profile',
                             kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый текст',
                group=self.group.pk,
                image='posts/small.gif',
            ).exists()
        )

    def test_post_create(self):
        """Проверяем, что создаётся новая запись в базе данных."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('post:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Текст поста',
                group=self.group.pk,
            ).exists()
        )

    def test_guest_user_cannot_publish_post(self):
        """Проверяем, что не создаётся новая запись,
        если пользователь не зарегистрирован.
        """
        form_data = {
            'text':
            'Текст поста для проверки невозможности'
            'создания поста неавторизованным пользователем',
            'group': self.group.pk,
        }
        response = self.guest_client.post(reverse('post:post_create'),
                                          data=form_data,
                                          follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=%2Fcreate%2F')
        self.assertFalse(
            Post.objects.filter(
                author=self.user,
                text='Текст поста для проверки невозможности'
                     'создания поста неавторизованным пользователем',
                group=self.group.pk).exists())

    def test_post_edit(self):
        """Проверяем, что происходит изменение поста
        с post_id в базе данных.
        """
        form_data = {
            'group': self.group.pk,
            'text': 'Поста текст',
        }
        response = self.authorized_client.post(
            reverse('post:update_post', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Поста текст',
                group=self.group.pk,
            ).exists()
        )

    def test_label(self):
        """Проверяем lable."""
        text_label = PostCreateFormTests.form.fields['text'].label
        group_label = PostCreateFormTests.form.fields['group'].label
        self.assertTrue(text_label, 'Текст поста')
        self.assertTrue(group_label, 'Группа поста')

    def test_help(self):
        """Проверяем help."""
        text_help = PostCreateFormTests.form.fields['text'].help_text
        group_help = PostCreateFormTests.form.fields['group'].help_text
        self.assertTrue(text_help, 'Напишите текст поста')
        self.assertTrue(group_help, 'Выберите группу для поста')

    def test_signup(self):
        """Проверяем, что создаётся новый пользователь."""
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
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
