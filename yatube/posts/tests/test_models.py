from django.test import TestCase
from django.conf import settings

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some_group',
            description='Тестовое описание',)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        self.assertEqual(str(post), post.text[:settings.POST_TEXT_SHORT])

        group = self.group
        self.assertEqual(str(group), group.title)

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        fields_verboses = {
            'text': 'Текст публикации',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for field, expected_value in fields_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        fields_help_texts = {
            'text': '* - обязательное поле. Введите текст'
            'публикации, не более 2000 символов.',
            'author': 'Выберите автора публикации.',
            'group': 'Выберите группу к которой будет '
                      'относиться запись.',
        }
        for field, expected_value in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
