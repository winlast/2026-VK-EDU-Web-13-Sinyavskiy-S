from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from .models import Answer, AnswerLike, Question, QuestionLike, Tag
from .utils import paginate


class PaginateTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.items = list(range(25))  # 3 страницы по 10

    def get_page(self, page_param):
        request = self.factory.get('/', {'page': page_param})
        return paginate(self.items, request)

    def test_default_page(self):
        page = paginate(self.items, self.factory.get('/'))
        self.assertEqual(page.number, 1)
        self.assertEqual(list(page), list(range(10)))

    def test_valid_page(self):
        self.assertEqual(self.get_page('2').number, 2)

    def test_not_integer_page(self):
        for value in ['abc', '1.5', '']:
            self.assertEqual(self.get_page(value).number, 1)

    def test_too_big_page(self):
        self.assertEqual(self.get_page('100').number, 3)

    def test_zero_and_negative_page(self):
        self.assertEqual(self.get_page('0').number, 1)
        self.assertEqual(self.get_page('-5').number, 1)

    def test_per_page(self):
        request = self.factory.get('/')
        self.assertEqual(len(paginate(self.items, request, per_page=5)), 5)


class PagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(username='author')
        cls.question = Question.objects.create(author=author, title='Python в ИУ5', text='Пример.')
        cls.question.tags.add(Tag.objects.create(name='python'))

    def setUp(self):
        cache.clear()

    def test_pages_open(self):
        urls = [
            reverse('index'),
            reverse('hot'),
            reverse('tag', args=['python']),
            self.question.get_absolute_url(),
            reverse('ask'),
            reverse('login'),
            reverse('signup'),
            reverse('profile'),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_bad_page_param(self):
        response = self.client.get(reverse('index'), {'page': 'abc'})
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        self.assertEqual(self.client.get(reverse('question', args=[100500])).status_code, 404)
        self.assertEqual(self.client.get(reverse('tag', args=['нет-такого'])).status_code, 404)


class DataTests(TestCase):
    def test_fill_db_adds_exact_counts_and_can_be_repeated(self):
        for runs in (1, 2):
            call_command('fill_db', 2, stdout=StringIO())
            self.assertEqual(get_user_model().objects.count(), 2 * runs)
            self.assertEqual(Question.objects.count(), 20 * runs)
            self.assertEqual(Answer.objects.count(), 200 * runs)
            self.assertEqual(Tag.objects.count(), 2 * runs)
            self.assertEqual(QuestionLike.objects.count() + AnswerLike.objects.count(), 400 * runs)

    def test_list_queries_do_not_grow_with_number_of_questions(self):
        author = get_user_model().objects.create_user(username='author')
        Question.objects.create(author=author, title='Вопрос', text='Текст')
        cache.clear()
        self.client.get(reverse('index'))
        with self.assertNumQueries(3):
            self.client.get(reverse('index'))
        Question.objects.bulk_create([
            Question(author=author, title=f'Вопрос {i}', text='Текст') for i in range(20)
        ])
        with self.assertNumQueries(3):
            self.client.get(reverse('index'))


class HeaderTests(TestCase):
    def test_guest_header(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('login'))
        self.assertContains(response, reverse('signup'))
        self.assertNotContains(response, reverse('logout'))

    def test_user_header(self):
        user = get_user_model().objects.create_user(username='stanislav')
        self.client.force_login(user)
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'stanislav')
        self.assertContains(response, reverse('logout'))

    def test_logout(self):
        user = get_user_model().objects.create_user(username='stanislav')
        self.client.force_login(user)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('index'))
