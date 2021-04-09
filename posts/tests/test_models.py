from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Group, Post, Follow

User = get_user_model()


class PostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_username')
        cls.follower = User.objects.create_user(username='follower')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            text='test text',
            author=cls.user,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.user
        )

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Ключ',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_verbose_name_post(self):
        """Проверка названия полей, модели Post"""
        post = PostTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_group(self):
        """Проверка подсказки для модели Group"""
        group = PostTest.group
        help_text = group._meta.get_field('slug').help_text
        expected_help_text = ('Для ссылки на вашу группу. '
                              'Пишите Латиницей без пробелов')
        self.assertEqual(help_text, expected_help_text)

    def test_str_group(self):
        """Проверка строчного значения объекта Group"""
        group = PostTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))

    def test_help_text_post(self):
        """Проверка подсказки для модели Post"""
        post = PostTest.post
        help_text = post._meta.get_field('group').help_text
        expected_help_text = 'Группа, в которой публикуется запись'
        self.assertEqual(help_text, expected_help_text)

    def test_str_post(self):
        """
        В поле __str__  объекта post записано значение поля post.text[:15].
        """
        post = PostTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))

    def test_comment_model(self):
        comment = self.comment
        field_verboses = {
            'post': 'Пост',
            'created': 'Дата публикации',
            'author': 'Автор',
            'text': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_follow_model(self):
        self.assertTrue(self.follower.follower.count() > 0)
        self.assertTrue(self.user.following.count() > 0)

    # def test_follow_model(self):
    #     count_follow = Follow.objects.count()
    #     Follow.objects.create(user=self.user, author=self.user)
    #     try:
    #         Follow.objects.create(user=self.user, author=self.user)
    #     except:
    #         self.assertEqual(Follow.objects.count(), count_follow + 1)
