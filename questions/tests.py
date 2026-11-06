from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

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


class PagesTests(SimpleTestCase):
    def test_pages_open(self):
        urls = [
            reverse('index'),
            reverse('hot'),
            reverse('tag', args=['python']),
            reverse('question', args=[1]),
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
