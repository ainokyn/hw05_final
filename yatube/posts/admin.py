from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    """Class that configures the display of Post  model. """
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Class that configures the display of Group  model. """
    list_display = ('pk', 'title', 'description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Class that configures the display of Comment model. """
    list_display = ('pk', 'author', 'text', 'created',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Class that configures the display of Follow model. """
    list_display = ('pk', 'author', 'user',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
