from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='PostAuthor')
        cls.user_not_author = User.objects.create_user(username='NotAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',)
        cls.guest = Client()
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.auth_user_not_author = Client()
        cls.auth_user_not_author.force_login(cls.user_not_author)

    def test_not_existing_path(self):
        """Проверка, что запрос к несуществующей странице вернёт
        ошибку 404 и соответствующий шаблон."""
        users = [self.guest, self.auth_user]

        for user in users:
            response = user.get('/not_existing_path/')
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
            self.assertTemplateUsed(response, 'core/404.html')

    def test_posts_urls_correct_template_and_availability_all_users(self):
        """Проверка использования URL-адресами соответствующего шаблона
        и доступности публичных страниц для всех пользователей."""
        urls_all_clients = [
            [reverse('posts:index'), 'posts/index.html'],
            [reverse('posts:group_list', kwargs={
                'slug': self.group.slug}), 'posts/group_list.html'],
            [reverse('posts:profile', kwargs={
                'username': self.user.username}), 'posts/profile.html'],
            [reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}), 'posts/post_detail.html'],
        ]
        users = [self.guest,
                 self.auth_user,
                 self.auth_user_not_author]
        for user in users:
            for url, template in urls_all_clients:
                with self.subTest(url=url):
                    response = user.get(url)
                    self.assertTemplateUsed(response, template)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_correct_template_and_OKstatus_without_redirect(self):
        """Проверка использования URL-адресами соответствующего шаблона
        и доступности страниц 'posts:post_create' и 'posts:post_edit' для
        пользователей без переадресации."""
        urls_without_redirects = [
            [reverse('posts:post_create'), 'posts/post_create.html',
             self.auth_user],
            [reverse('posts:post_create'), 'posts/post_create.html',
             self.auth_user_not_author],
            [reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}), 'posts/post_create.html',
             self.auth_user],
        ]
        for url, template, user in urls_without_redirects:
            with self.subTest(url=url):
                response = user.get(url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_correct_template_and_OKstatus_with_redirect(self):
        """Проверка использования URL-адресами соответствующего шаблона
        и доступности страниц 'posts:post_create' и 'posts:post_edit' для
        пользователей с переадресацией."""
        urls_redirects = [
            [reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}),
             self.auth_user_not_author,
             reverse('posts:post_detail', kwargs={
                 'post_id': self.post.id})],
            [reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}),
             self.guest,
             reverse('users:login') + '?next=' + reverse(
                 'posts:post_edit', kwargs={'post_id': self.post.id})],
            [reverse('posts:post_create'),
             self.guest,
             reverse('users:login') + '?next=' + reverse('posts:post_create')],
        ]
        for url, user, redirect_url in urls_redirects:
            with self.subTest(url=url):
                response = user.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, redirect_url)
