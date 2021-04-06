import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='fan-durov')
        cls.user = User.objects.create_user(username='durov')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        Group.objects.create(
            title='Тест',
            slug='test-slug',
            id=5
        )

        cls.group = Group.objects.create(
            title='ВКонтакте',
            slug='vk',
            description='Правительство в изгнании',
        )
        for i in range(15):
            Post.objects.create(
                text=str(i),
                author=cls.user,
                group=cls.group
            )
        Post.objects.create(
            text='Я не верну стену!',
            author=cls.user,
            group=cls.group,
            image=uploaded,
            pk=100
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', args=('vk',)),
            'new_post.html': reverse('new_post')
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                res = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(res, template)

    def test_objects_len_home_page(self):
        res = self.authorized_client.get(reverse('index'))
        response = res.context['page']
        expected = Post.objects.all()[:10]
        self.assertEqual(len(response), len(expected))

    def test_home_page_show_correct_context(self):
        res = self.authorized_client.get(reverse('index'))
        res_objects = res.context['page']
        expected_objects = Post.objects.all()[:10]
        for res, expected in zip(res_objects, expected_objects):
            with self.subTest(response=res):
                self.assertEqual(res, expected)

    def test_home_second_page_correct_length(self):
        res = self.authorized_client.get(
            reverse('index'),
            data={'page': 2}
        )
        self.assertEqual(len(res.context.get('page').object_list), 6)

    def test_objects_len_group_page(self):
        res = self.authorized_client.get(
            reverse('group_posts', args=('vk',)))
        response = res.context['page']
        expected = Post.objects.filter(group=self.group).all()[:10]
        self.assertEqual(len(response), len(expected))

    def test_objects_in_null_group(self):
        res = self.authorized_client.get(
            reverse('group_posts', args=('test-slug',)))
        responce = res.context['page']
        self.assertEqual(len(responce), 0)

    def test_group_page_show_correct_context(self):
        res = self.authorized_client.get(reverse('group_posts', args=('vk',)))
        res_objects = res.context['page']
        expected_objects = Post.objects.filter(group=self.group).all()[:10]
        for res, expected in zip(
                res_objects, expected_objects):
            with self.subTest(response=res):
                self.assertEqual(res, expected)

    def test_new_post_show_correct_context(self):
        res = self.authorized_client.get(
            reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(
                    res.context['form'].fields[value], expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post_edit', args=(self.user.username, 3)))
        expected = Post.objects.get(pk=3)
        context = response.context['post']
        self.assertEqual(context, expected)

    def test_profile_length(self):
        user = User.objects.get(username='durov')
        response = self.authorized_client.get(reverse(
            'profile', args=(user.username,)))
        response2 = self.authorized_client.get(
            reverse('profile', args=(user.username,)),
            data={'page': 2}
        )
        expected = Post.objects.filter(author=user).count()
        context = len(
            response.context['page']) + len(response2.context['page'])
        self.assertEqual(expected, context)

    def test_profile_show_correct_context(self):
        user = User.objects.get(username='durov')
        response = self.authorized_client.get(reverse(
            'profile', args=(user.username,)))
        expected = Post.objects.filter(author=user).all()[:10]
        context = response.context['page']
        for ex, con in zip(expected, context):
            with self.subTest(expected=ex):
                self.assertEqual(ex, con)

    def test_post_correct_context(self):
        user = User.objects.get(username='durov')
        response = self.authorized_client.get(
            reverse('post', args=(user.username, 100)))
        expected = Post.objects.get(pk=100)
        context = response.context['post']
        self.assertEqual(expected, context)

    def test_correct_show_content(self):
        response = self.authorized_client.get(reverse('index'))
        context = response.context['page']
        expected_list = Post.objects.all()[:10]
        for post, expected in zip(context, expected_list):
            with self.subTest(post=post):
                self.assertEqual(post.text, expected.text)
                self.assertEqual(post.author, expected.author)
                self.assertEqual(post.group, expected.group)

    def test_follow_authorized_client(self):
        response = self.follower_client.get(  # noqa
            reverse('profile_follow', args=(self.user.username,)))
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower, author=self.user).exists()
        )
        response = self.follower_client.get(  # noqa
            reverse('profile_unfollow', args=(self.user.username,)))
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower, author=self.user).exists()
        )

    def test_follow_index_follower(self):
        Post.objects.create(text='asd', author=self.follower)
        Follow.objects.create(user=self.follower, author=self.user)
        response = self.follower_client.get(
            reverse('follow_index'))
        context = response.context['page']
        expected = self.user.posts.all()[:10]
        for expected_post, post in zip(expected, context):
            with self.subTest(expected=expected_post):
                self.assertEqual(post, expected_post)

    def test_follow_index_null(self):
        response = self.authorized_client.get(reverse('follow_index'))
        context = response.context['page']
        self.assertEqual(len(context), 0)
