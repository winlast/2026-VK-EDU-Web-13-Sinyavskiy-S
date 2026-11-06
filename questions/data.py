"""
Данные-заглушки («рыба») для ДЗ2.

В ДЗ3 этот модуль заменится выборками из базы данных, поэтому
все данные отдаются через функции, а не напрямую через списки.
"""

import random
from datetime import datetime, timedelta

MEMBERS = [
    {'id': 1, 'name': 'Анна Королёва', 'avatar': 'core/img/avatar-1.svg'},
    {'id': 2, 'name': 'Максим Петров', 'avatar': 'core/img/avatar-2.svg'},
    {'id': 3, 'name': 'Илья Смирнов', 'avatar': 'core/img/avatar-3.svg'},
    {'id': 4, 'name': 'Екатерина Волкова', 'avatar': 'core/img/avatar-4.svg'},
    {'id': 5, 'name': 'Дмитрий Романов', 'avatar': 'core/img/avatar-5.svg'},
]

TAGS = [
    'python', 'django', 'сессия', 'ИУ5', 'технопарк',
    'матан', 'общага', 'c++', 'mysql', 'стипендия',
]

TITLES = [
    'Как поступить в Технопарк VK при Бауманке?',
    'Django или FastAPI для первого пет-проекта?',
    'Какие предметы на ИУ5 реально пригодятся в IT?',
    'Как не завалить матан в первую сессию?',
    'Почему MySQL ругается на кодировку при импорте дампа?',
    'Где в общаге нормально работает интернет?',
    'Как получить повышенную стипендию?',
    'С чего начать изучение C++ после Python?',
]

TEXTS = [
    'Учусь на втором курсе и хочу разобраться, с какой стороны подойти к задаче. '
    'Перечитал конспекты и пару статей, но картинка пока не складывается. '
    'Подскажите, что почитать и на что обратить внимание в первую очередь?',
    'Пробовал сделать сам, но застрял на середине: всё вроде бы по инструкции, '
    'а результат не тот. Может быть, кто-то уже сталкивался с похожим и знает, где подвох?',
    'Вопрос, наверное, глупый, но на семинаре объяснили слишком быстро. '
    'Буду благодарен за простое объяснение на пальцах и пару полезных ссылок.',
]

ANSWER_TEXTS = [
    'Сначала разберись с основами, потом всё пойдёт быстрее. Мне помогли '
    'записи лекций прошлых лет и разбор задач на семинарах.',
    'Сталкивался с тем же. Проблема была в настройках, после переустановки всё заработало.',
    'Посмотри официальную документацию, там есть хороший туториал с примерами.',
    'Лучше спросить у семинариста на консультации, он подробно объясняет такие вещи.',
    'Попробуй разбить задачу на части и решать по одной, так проще найти ошибку.',
]

_NOW = datetime(2026, 11, 7, 12, 0)


def _make_questions(count=60):
    rnd = random.Random(42)
    questions = []
    for i in range(1, count + 1):
        title = TITLES[(i - 1) % len(TITLES)]
        questions.append({
            'id': i,
            'title': f'{title} #{i}',
            'text': TEXTS[i % len(TEXTS)],
            'author': MEMBERS[i % len(MEMBERS)],
            'tags': rnd.sample(TAGS, rnd.randint(1, 3)),
            'rating': rnd.randint(-5, 40),
            'vote': rnd.choice(['up', 'down', None, None]),
            'answers_count': rnd.randint(0, 14),
            'created_at': _NOW - timedelta(hours=i * 5 + rnd.randint(0, 4)),
        })
    return questions


QUESTIONS = _make_questions()


def get_new_questions():
    return QUESTIONS


def get_hot_questions():
    return sorted(QUESTIONS, key=lambda q: q['rating'], reverse=True)


def get_questions_by_tag(tag_name):
    return [q for q in QUESTIONS if tag_name in q['tags']]


def get_question(question_id):
    for question in QUESTIONS:
        if question['id'] == question_id:
            return question
    return None


def get_answers(question):
    rnd = random.Random(question['id'])
    answers = []
    for i in range(1, question['answers_count'] + 1):
        answers.append({
            'id': question['id'] * 100 + i,
            'text': ANSWER_TEXTS[(question['id'] + i) % len(ANSWER_TEXTS)],
            'author': MEMBERS[(question['id'] + i) % len(MEMBERS)],
            'rating': rnd.randint(-3, 15),
            'vote': rnd.choice(['up', 'down', None, None]),
            'is_correct': i == 1,
            'created_at': question['created_at'] + timedelta(minutes=i * 37),
        })
    return answers


def get_popular_tags():
    return TAGS


def get_best_members():
    return MEMBERS
