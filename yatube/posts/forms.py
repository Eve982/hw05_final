from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = {'text': '* - обязательное поле. Введите текст '
                            'публикации, не более 2000 символов.',
                      'group': 'Выберите группу к которой будет '
                              'относиться запись.',
                      'image': 'Загрузите изображение'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
