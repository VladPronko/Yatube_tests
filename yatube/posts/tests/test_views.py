from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

        paginator_posts = 13
        for posts in range(paginator_posts):
            Post.objects.create(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group,)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        urls_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/post_create.html'
        }
        for reverse_name, template in urls_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_group_posts_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test_slug'}))
        post = response.context['page_obj'][0]
        self.assertEqual(post.group, self.post.group)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        post = response.context['page_obj'][0]
        self.assertEqual(post.author, self.post.author)

    def test_post_detail_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        post = response.context['post'].pk
        self.assertEqual(post, self.post.pk)

    def test_post_create_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context['form'].fields[value]
                self.assertIsInstance(field, expected)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context['form'].fields[value]
                self.assertIsInstance(field, expected)

    def test_index_contains_ten_records(self):
        urls_with_paginator = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={
                'username': PostsPagesTests.user.username}),
        )
        for urls in urls_with_paginator:
            response = self.authorized_client.get(urls)
            self.assertEqual(len(response.context['page_obj']), 10)
