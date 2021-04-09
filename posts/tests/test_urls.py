from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus
from posts import models

User = get_user_model()


class TestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='anakentii')
        other_author = User.objects.create(username='NeA')
        group = models.Group.objects.create(
            title='Группа',
            slug='test-slug',
            description='Тестовая группа'
        )
        cls.post1 = models.Post.objects.create(
            text='май найм итз Анакентий',
            author=cls.user,
            group=group,
            id=10
        )
        cls.post2 = models.Post.objects.create(
            text='Я не Анакентий!',
            author=other_author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TestUrls.user)

    def test_page_accessibility_guest(self):
        """Достпность страниц для гостя"""
        url_names = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/new/': HTTPStatus.FOUND,
            '/anakentii/': HTTPStatus.OK,
            f'/NeA/{TestUrls.post2.id}/': HTTPStatus.OK,
            f'/NeA/{TestUrls.post2.id}/edit/': HTTPStatus.FOUND,
        }
        for url, code in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_test_page_accessibility_authorized(self):
        url_names = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/new/': HTTPStatus.OK,
            '/anakentii/': HTTPStatus.OK,
            f'/NeA/{TestUrls.post2.id}/': HTTPStatus.OK,
            f'/NeA/{TestUrls.post2.id}/comment/': HTTPStatus.FOUND,
            f'/{TestUrls.user.username}/'
            f'{TestUrls.post1.id}/edit/': HTTPStatus.OK,
            f'/NeA/{TestUrls.post2.id}/edit/': HTTPStatus.FOUND,
        }
        for url, code in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_template(self):
        template_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/new/': 'new_post.html',
            f'/{TestUrls.user.username}/'
            f'{TestUrls.post1.id}/edit/': 'new_post.html',
            f'/{TestUrls.user.username}/': 'profile.html',
        }

        for reverse_name, template in template_url_names.items():
            with self.subTest(template=template):
                res = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(res, template)

    def test_redirect_gust(self):
        url_redirect_names = {
            '/anakentii/10/edit/': '/auth/login/?next=/anakentii/10/edit/',
        }
        for url, redirect in url_redirect_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect)

    def test_404_code(self):
        url = '/imposible/tag'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_follow_usrls(self):
        urls = [
            f'/{self.user.username}/follow/',
            f'/{self.user.username}/unfollow/',
            f'/{self.user.username}/unfollow/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, f'/{self.user.username}/')
