import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Post

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class TestFormPost(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='andrej')
        Post.objects.create(
            text='test_killer 1.0',
            author=cls.user,
            id=1
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_new_post_from_guest(self):
        expected = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст'
        }
        self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        post_count = Post.objects.count()
        self.assertEqual(post_count, expected)

    def test_form_new_post(self):
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Не создалась запись в БД')

    def test_form_edit(self):
        form_data = {
            'text': 'test_killer 2.0'
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=(self.user.username, 1)),
            data=form_data,
            follow=True
        )
        object = Post.objects.get(id=1)
        expected = 'test_killer 2.0'
        self.assertRedirects(response, reverse('post', args=[
            self.user.username, 1]))
        self.assertEqual(object.text, expected)

    def test_image(self):
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'test text РУс',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='test text РУс',
                image='posts/small.gif'
            ).exists()
        )

    def test_comment_authoreized_client(self):
        count = Comment.objects.count()
        form_data = {
            'text': 'Not tuday!'
        }
        response = self.authorized_client.post(  # noqa
            reverse('add_comment', args=(self.user.username, 1)),
            form_data,
            follow=True
        )
        response
        self.assertEqual(Comment.objects.count(), count + 1)
        self.assertEqual(
            Comment.objects.get(author=self.user).text, form_data['text'])

    def test_comment_guest_client(self):
        count = Comment.objects.count()
        form_data = {
            'text': 'Not tuday!'
        }
        response = self.guest_client.post(  # noqa
            reverse('add_comment', args=(self.user.username, 1)),
            form_data,
            follow=True
        )
        response
        self.assertEqual(Comment.objects.count(), count)
