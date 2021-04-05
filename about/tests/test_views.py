from django.test import TestCase
from django.test.client import Client
from django.urls import reverse


class TestViewsAbout(TestCase):

    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_views(self):
        reverse_names = {
            reverse('about:author'): 'about_author.html',
            reverse('about:tech'): 'about_tech.html',
        }
        for url, template in reverse_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
