# Generated by Django 2.2.16 on 2021-09-08 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0023_auto_20210908_1633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created'], 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='pub_date',
            new_name='created',
        ),
        migrations.RemoveField(
            model_name='follow',
            name='pub_date',
        ),
    ]
