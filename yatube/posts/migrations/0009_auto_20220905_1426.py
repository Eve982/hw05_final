# Generated by Django 2.2.6 on 2022-09-05 14:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20220904_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Описание группы', verbose_name='Описание группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='Укажите уникальный адрес для страницы задачи. Используйте только латиницу, цифры, дефисы и знаки подчёркивания', unique=True, verbose_name='Идентификатор'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Название группы', max_length=200, verbose_name='Название группы'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(help_text='Автор', on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Описание группы', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Сообщество'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Текст публикации', max_length=2000, verbose_name='Текст публикации'),
        ),
    ]