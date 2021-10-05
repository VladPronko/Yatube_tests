from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

        cls.urls_templates_guest = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
                'posts/post_detail.html',
        }
        cls.urls_templates_user = {
            # reverse('posts:post_edit'): 'posts/post_create.html',
            # уже проверили в test_author_post_edit
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        cls.urls_templates = {
            **cls.urls_templates_guest, **cls.urls_templates_user}

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_public_pages(self):
        """Проверяем доступность страниц неавторизованному пользователю"""
        for address in URLTests.urls_templates_guest:
            with self.subTest(field=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_urls_user_pages(self):
        """Проверяем доступность страниц всех страниц"""
        """для авторизованного пользователя"""
        for address in URLTests.urls_templates:
            with self.subTest(field=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_redirect_urls_user_pages(self):
        """Проверяем редирект неавторизованного пользователя на"""
        """страницах create и edit"""
        for address in URLTests.urls_templates_user:
            with self.subTest(field=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in URLTests.urls_templates_guest.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_author_post_edit(self):
        """Страница post_edit доступна автору."""
        post_author = Client()
        post_author.force_login(URLTests.user)
        post_author_url = reverse('posts:post_edit', kwargs={'post_id': 1})
        response = post_author.get(post_author_url)
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Проверяем,что запрос к несуществующей странице вернёт ошибку 404."""
        response = self.guest_client.get('2224rwfw2/')
        self.assertEqual(response.status_code, 404)
