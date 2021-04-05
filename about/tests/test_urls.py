from django.test import TestCase
from django.test.client import Client


class TestUrlsAbout(TestCase):

    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_page_accessibility_guest(self):
        url_names = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_template(self):
        url_temp_names = {
            '/about/author/': 'about_author.html',
            '/about/tech/': 'about_tech.html'
        }
        for url, temp in url_temp_names.items():
            response = self.guest_client.get(url)
            self.assertTemplateUsed(response, temp)
