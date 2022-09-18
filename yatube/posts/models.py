from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Название группы',
                             max_length=200,
                             help_text='Укажите название группы.')
    slug = models.SlugField('Идентификатор',
                            unique=True,
                            help_text='Укажите уникальный адрес для страницы '
                            'задачи. Используйте только '
                            'латиницу, цифры, дефисы и знаки подчёркивания.')
    description = models.TextField('Описание группы',
                                   help_text='Опишите группу.')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группу"
        verbose_name_plural = "Группы"


class Post(CreatedModel):
    text = models.TextField('Текст публикации',
                            max_length=2000,)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор',)

    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts',
                              verbose_name='Сообщество',)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    def __str__(self):
        return self.text[:settings.POST_TEXT_SHORT]

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Публикацию"
        verbose_name_plural = "Публикации"


class Comment(CreatedModel):
    post = models.ForeignKey(Post,
                             verbose_name='Пост',
                             related_name='comments',
                             on_delete=models.CASCADE,)
    author = models.ForeignKey(User,
                               verbose_name='Автор комментария',
                               related_name='comments',
                               on_delete=models.CASCADE,)
    text = models.TextField('Текст комментария',
                            max_length=2000,)

    class Meta:
        ordering = ('pub_date',)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Подписчик',
                             related_name='follower',
                             on_delete=models.CASCADE,)
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               related_name='following',
                               on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'