from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_username')

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
