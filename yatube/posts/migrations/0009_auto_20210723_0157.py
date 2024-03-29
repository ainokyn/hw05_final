# Generated by Django 2.2.9 on 2021-07-22 22:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20210721_2303'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, null=True, unique=True, verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='groups', to='posts.Group'),
        ),
    ]
