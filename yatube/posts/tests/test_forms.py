from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.user = User.objects.create(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text'
        )
        cls.form = PostForm()

    def setUp(self):
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={
                'username': PostFormTests.user.username}),
            HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.all()[0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_unauthorized_client_cannot_create_post_(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        response = self.unauthorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/', HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_edit(self):
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}), HTTPStatus.FOUND)
        post = Post.objects.all()[0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
