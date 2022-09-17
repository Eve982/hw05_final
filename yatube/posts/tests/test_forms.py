from http import HTTPStatus
from django.core.cache import cache
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, User, Group, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Ненавистников тестирования',
            slug='test_group',
            description='Ненавидим тестирование, но начинаем любить.. УЖС!',)
        cls.author = User.objects.create_user(
            username='hater',
            first_name='Тест',
            last_name='Ненавистный',
            email='hate@hate.ru')
        cls.post = Post.objects.create(
            group=cls.group,
            text="Ненавистный тестовый текст:)бггг бесит",
            author=cls.author)
        cls.uploaded = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                        b'\x01\x00\x80\x00\x00\x00\x00\x00'
                        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                        b'\x0A\x00\x3B')
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.uploaded,
            content_type='image/gif')
        cls.guest = Client()
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.author)
        cls.comment = {
            'text': 'Тестовый комментарий авторизованного пользователя'}

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_new_post(self):
        """Проверка создания нового поста в конкретной группе БД."""
        posts_count = Post.objects.count()
        group_posts_count = Post.objects.filter(group_id=self.group.id).count()
        create_post_form_data = {
            'group': self.group.id,
            'author': self.author,
            'text': 'Тестовый текст',
            'image': self.image,
        }

        response = self.auth_user.post(reverse('posts:post_create'),
                                       data=create_post_form_data,
                                       follow=True)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.author.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.filter(group_id=self.group.id).count(),
                         group_posts_count + 1)
        self.assertTrue(Post.objects.filter(
            group=self.group.id,
            author=self.author,
            text='Тестовый текст',
        ).exists())
        self.assertEqual(list(create_post_form_data['image'].chunks()),
                         list(self.image.chunks()))

    def test_edit_post(self):
        """Проверка редактирования существующего поста в БД."""
        posts_count = Post.objects.count()
        edit_post_form_data = {
            'text': 'Редактируем текст',
            'group': self.group.id,
        }
        response = self.auth_user.post(reverse('posts:post_edit', kwargs={
            'post_id': self.post.id, }), data=edit_post_form_data, follow=True)

        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(text='Редактируем текст',
                                            group=self.group,
                                            ).exists())

    def test_permitions_to_comment_by_authorized_user(self):
        """Комментировать посты может только зарегистрированный
        пользователь, комментарий появляется на странице поста."""
        comment_count = Comment.objects.count()
        response = self.auth_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': 'Новый комментарий.'}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Новый комментарий.').exists())

    def test_permitions_to_comment_by_guest(self):
        """Комментирование недоступно анонимному пользователю."""
        response = self.guest.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=self.comment)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_is_in_cache_after_deleting(self):
        """При удалении поста из БД, она остается в response.content
        до принудительной очистки кэша."""
        response1 = self.auth_user.get(reverse('posts:index'))
        Post.objects.get(pk=1).delete()
        response2 = self.auth_user.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.auth_user.get(reverse('posts:index'))
        self.assertNotEqual(response1.content, response3.content)
