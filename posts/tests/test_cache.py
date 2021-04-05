import time

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class testCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='nikto')
        Post.objects.create(
            text='Oba Boba',
            author=cls.user
        )

    def test_show_post_in_index(self):
        response = self.guest_client.get(reverse('index'))
        Post.objects.create(
            text='Obi Bobi',
            author=self.user
        )
        context = response.context['page']
        self.assertEqual(len(context), 1)
        time.sleep(20)
        response = self.guest_client.get(reverse('index'))
        context = response.context['page']
        self.assertEqual(len(context), 2)
