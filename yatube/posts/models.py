from django.contrib.auth import get_user_model
from django.db import models
from core.core.models import CreatedModel

class Group(models.Model):
    """Description of the Group model."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL",
                            null=True, blank=True)
    description = models.TextField()

    class Meta:
        """Performs sorting."""
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


User = get_user_model()
"""Accessing the User model."""


class Post(CreatedModel):
    """Description of the Post model."""
    text = models.TextField('Текст поста', help_text='Напишите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name='posts', blank=True, null=True,
                              help_text='Выберите группу для поста',
                              verbose_name='Группа поста')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Performs sorting."""
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('Текст', help_text='Текст нового комментария')

    class Meta:
        """Performs sorting."""
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        """Performs sorting."""
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
