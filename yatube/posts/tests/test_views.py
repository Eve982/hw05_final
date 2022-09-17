import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms

from posts.models import Post, User, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Ненавистников тестирования',
            slug='test_group',
            description='Ненавидим тестирование, но начинаем любить.. УЖС!',)
        cls.group1 = Group.objects.create(
            title='someTitle',
            slug='some_group',
            description='hate',)
        cls.author = User.objects.create_user(
            username='hater',
            first_name='Тест',
            last_name='Ненавистный',
            email='hate@hate.ru')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B',
            content_type='image/gif')
        cls.post = Post.objects.create(
            group=cls.group,
            text="Текст:)",
            author=cls.author,
            image=cls.uploaded,)
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.author)
        cls.responses = {
            'index': cls.auth_user.get(reverse('posts:index')),
            'profile': cls.auth_user.get(reverse('posts:profile', kwargs={
                'username': cls.author.username})),
            'group_list': cls.auth_user.get(reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug})),
            'post_detail': cls.auth_user.get(reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id})),
            'post_create': cls.auth_user.get(reverse('posts:post_create')),
            'post_edit': cls.auth_user.get(reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}))
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_new_post_rendered_at_correct_pages(self):
        """Новый пост отображается на нужных страницах."""
        url_response_without_post = self.auth_user.get(reverse(
            'posts:group_list', kwargs={'slug': self.group1.slug}))
        self.assertNotIn(
            self.post, url_response_without_post.context['page_obj'])

        for name, response in self.responses.items():
            with self.subTest(response=response):
                if name in ('index', 'profile', 'group_list'):
                    self.assertIn(self.post, response.context['page_obj'])
                elif name in ('post_detail'):
                    self.assertEqual(self.post, response.context['post'])

    def test_pages_with_posts_show_correct_context(self):
        """Шаблоны 'index', 'group_list' и 'post_detail' сформированы
        с правильным контекстом."""
        for name, response in self.responses.items():
            with self.subTest(response=response):
                if name in ('index', 'group_list'):
                    first_object = response.context['page_obj'][0]
                    self.assertEqual(first_object.text, 'Текст:)')
                    self.assertEqual(first_object.author.username, 'hater')
                    self.assertEqual(first_object.group.slug, 'test_group')
                elif name in ('post_detail'):
                    self.assertEqual(
                        response.context.get('post').text, 'Текст:)')
                    self.assertEqual(
                        response.context.get('post').author.username, 'hater')
                    self.assertEqual(response.context.get('post').group.slug,
                                     'test_group')

    def test_post_create_page_show_correct_context(self):
        """Шаблоны post_create, post_edit сформированы с правильным
        контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
        }
        for name, response in self.responses.items():
            if name in ('post_create', 'post_edit'):
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form').fields.get(value)
                        self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.author = User.objects.create_user(username='SomeAuthor')
        cls.group = Group.objects.create(
            title='Последний тест',
            description='надоело',
            slug='hate-slug')
        Post.objects.bulk_create(
            Post(text=f'Some post text №{i}',
                 author=cls.author, group=cls.group)
            for i in range(13))
        cls.url_pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.author.username}),
        )

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        LAST_PAGE_POSTS_AMOUNT = 3

        for url in self.url_pages:
            with self.subTest(url=url):
                self.assertEqual(len(self.guest.get(
                    url).context.get('page_obj')),
                    settings.POSTS_AMOUNT)
                self.assertEqual(len(self.guest.get(
                    url + '?page=2').context.get('page_obj')),
                    LAST_PAGE_POSTS_AMOUNT)
