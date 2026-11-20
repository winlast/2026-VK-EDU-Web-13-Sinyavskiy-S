from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, SimpleTestCase, TestCase
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
            reverse('login'),
            reverse('signup'),
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


class WriteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.author = users.create_user(username='author')
        cls.member = users.create_user(username='member')
        cls.question = Question.objects.create(author=cls.author, title='Вопрос', text='Текст')
        cls.answer = Answer.objects.create(question=cls.question, author=cls.member, text='Один ответ')

    def test_ask_rejects_invalid_tags_and_saves_valid_question(self):
        ask = reverse('ask')
        self.assertEqual(self.client.get(ask).status_code, 302)
        self.client.force_login(self.member)
        data = {'title': 'Новый вопрос', 'text': 'Его текст', 'tags': 'один, два, три, четыре'}
        failed = self.client.post(ask, data)
        self.assertTrue(failed.context['form'].errors.get('tags'))
        self.assertContains(failed, 'Новый вопрос')
        response = self.client.post(ask, {**data, 'tags': ' Python, python, иу5 '})
        item = Question.objects.get(title='Новый вопрос')
        self.assertRedirects(response, item.get_absolute_url())
        self.assertEqual(item.author, self.member)
        self.assertEqual(set(item.tags.values_list('name', flat=True)), {'python', 'иу5'})

    def test_answer_appears_on_correct_page(self):
        QuestionLike.objects.create(question=self.question, user=self.author, value=1)
        answers = Answer.objects.bulk_create([
            Answer(question=self.question, author=self.author, text=f'Старый ответ {i}')
            for i in range(31)
        ])
        AnswerLike.objects.bulk_create([
            AnswerLike(answer=answer, user=self.member, value=1) for answer in answers
        ])
        url = self.question.get_absolute_url()
        self.assertEqual(self.client.post(url, {'text': 'Гость'}).status_code, 302)
        self.client.force_login(self.member)
        failed = self.client.post(url, {'text': '   '})
        self.assertTrue(failed.context['form'].errors.get('text'))
        result = self.client.post(url, {'text': 'Новый ответ'})
        new_answer = Answer.objects.get(text='Новый ответ')
        self.assertRedirects(result, f'{url}?page=2#answer-{new_answer.pk}')
        self.assertContains(self.client.get(f'{url}?page=2'), f'id="answer-{new_answer.pk}"')

    def test_vote_can_be_repeated_changed_or_removed(self):
        url = reverse('vote-question', args=[self.question.pk])
        self.assertEqual(self.client.post(url, {'value': 1}).status_code, 401)
        self.client.force_login(self.member)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {'value': 2}).status_code, 400)
        self.assertEqual(Client(enforce_csrf_checks=True).post(url, {'value': 1}).status_code, 403)
        for value in (1, 1, -1, 0):
            response = self.client.post(url, {'value': value})
            self.assertEqual(response.json(), {'rating': value, 'value': value})
            self.assertEqual(QuestionLike.objects.filter(question=self.question).count(), bool(value))
        answer_url = reverse('vote-answer', args=[self.answer.pk])
        self.assertEqual(self.client.post(answer_url, {'value': -1}).json(), {'rating': -1, 'value': -1})
        self.assertContains(self.client.get(self.question.get_absolute_url()), 'aria-pressed="true"')

    def test_only_question_author_can_mark_one_answer(self):
        url = reverse('correct-answer', args=[self.question.pk, self.answer.pk])
        self.client.force_login(self.member)
        self.assertEqual(self.client.post(url, {'correct': 'true'}).status_code, 403)
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(url, {'correct': 'unexpected'}).status_code, 400)
        self.assertEqual(self.client.post(url, {'correct': 'true'}).json()['correct_answer_id'], self.answer.pk)
        second = Answer.objects.create(question=self.question, author=self.member, text='Второй ответ')
        url = reverse('correct-answer', args=[self.question.pk, second.pk])
        self.assertEqual(self.client.post(url, {'correct': 'true'}).json()['correct_answer_id'], second.pk)
        self.answer.refresh_from_db()
        self.assertFalse(self.answer.is_correct)
        self.assertIsNone(self.client.post(url, {'correct': 'false'}).json()['correct_answer_id'])
        other = Question.objects.create(author=self.author, title='Другой вопрос', text='Текст')
        url = reverse('correct-answer', args=[other.pk, self.answer.pk])
        self.assertEqual(self.client.post(url, {'correct': 'true'}).status_code, 404)
