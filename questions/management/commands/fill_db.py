from datetime import timedelta
from random import Random
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


BATCH_SIZE = 5000
QUESTION_BATCH_SIZE = 500
TOPICS = (
    ('первокурсники', 'Как подготовиться к первой сессии?'),
    ('иу5', 'Какие предметы на ИУ5 полезны для стажировки?'),
    ('технопарк', 'Как подготовиться к отбору на программу VK Education?'),
    ('электротехника', 'Как проверить схему перед защитой лабораторной?'),
    ('python', 'Как выбрать тему проекта на Python?'),
    ('общежитие', 'Что взять с собой в общежитие?'),
    ('django', 'Как организовать приложения Django в учебном проекте?'),
    ('стипендия', 'Где узнать условия повышенной стипендии?'),
    ('алгоритмы', 'Как проверять сложность алгоритма на практике?'),
    ('практика', 'Как выбрать место для летней практики?'),
)
ANSWERS_PER_TOPIC = (40, 0, 7, 8, 7, 8, 7, 8, 7, 8)


def users_and_tags(ratio, fake, run_id):
    user_model = get_user_model()
    users = user_model.objects.bulk_create([
        user_model(
            username=f'demo-{run_id}-{i}', first_name=fake.first_name(),
            email=f'{run_id}-{i}@example.invalid', password=make_password(None),
        )
        for i in range(ratio)
    ], batch_size=BATCH_SIZE)
    Profile.objects.bulk_create(
        [Profile(user_id=user.pk) for user in users], batch_size=BATCH_SIZE,
    )
    common = [
        Tag.objects.get_or_create(name=name) for name, _ in TOPICS[:min(len(TOPICS), ratio)]
    ]
    new_common_count = sum(created for _, created in common)
    tags = Tag.objects.bulk_create([
        Tag(name=f'{TOPICS[i % len(TOPICS)][0]}-{run_id}-{i}')
        for i in range(ratio - new_common_count)
    ], batch_size=BATCH_SIZE)
    common_ids = [tag.pk for tag, _ in common]
    return [user.pk for user in users], [tag.pk for tag in tags] + common_ids, common_ids


def votes(model, target, objects, users, counts, rng):
    rows = []
    for obj, count in zip(objects, counts):
        start = rng.randrange(len(users))
        for offset in range(count):
            rows.append(model(
                **{f'{target}_id': obj.pk}, user_id=users[(start + offset) % len(users)],
                value=rng.choice((1, 1, 1, -1)),
            ))
            if len(rows) == BATCH_SIZE:
                model.objects.bulk_create(rows)
                rows.clear()
    if rows:
        model.objects.bulk_create(rows)


def populate(ratio):
    fake = Faker('ru_RU')
    rng = Random()
    details = [fake.paragraph(nb_sentences=3) for _ in range(400)]
    replies = [fake.paragraph(nb_sentences=2) for _ in range(400)]
    users, tags, common_tags = users_and_tags(ratio, fake, uuid4().hex[:12])
    question_votes = min(ratio, 10)
    answer_votes, extra_votes = divmod(200 * ratio - question_votes * 10 * ratio, 100 * ratio)
    through = Question.tags.through
    answer_offset = 0
    now = timezone.now()

    for start in range(0, 10 * ratio, QUESTION_BATCH_SIZE):
        numbers = range(start, min(start + QUESTION_BATCH_SIZE, 10 * ratio))
        questions = Question.objects.bulk_create([
            Question(
                author_id=rng.choice(users), title=TOPICS[i % len(TOPICS)][1],
                created_at=now - timedelta(days=i % 365, hours=2),
                text=f'{rng.choice(details)}\n\nОбсуждение №{i + 1}.',
            )
            for i in numbers
        ], batch_size=BATCH_SIZE)
        through.objects.bulk_create([
            through(question_id=question.pk, tag_id=tag)
            for i, question in zip(numbers, questions)
            for tag in {tags[i % len(tags)], common_tags[i % len(common_tags)]}
        ], batch_size=BATCH_SIZE)
        votes(QuestionLike, 'question', questions, users, [question_votes] * len(questions), rng)

        answers = Answer.objects.bulk_create([
            Answer(question_id=question.pk, author_id=rng.choice(users), text=rng.choice(replies),
                   created_at=question.created_at + timedelta(minutes=n + 1),
                   is_correct=(n == 0 and i % 3 == 0))
            for i, question in zip(numbers, questions)
            for n in range(ANSWERS_PER_TOPIC[i % len(ANSWERS_PER_TOPIC)])
        ], batch_size=BATCH_SIZE)
        counts = [
            answer_votes + (answer_offset + i < extra_votes) for i in range(len(answers))
        ]
        votes(AnswerLike, 'answer', answers, users, counts, rng)
        answer_offset += len(answers)


class Command(BaseCommand):
    help = 'Добавляет тестовые данные форума пакетами.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio < 2:
            raise CommandError('Укажите ratio не меньше 2: одного пользователя недостаточно для уникальных оценок.')
        with transaction.atomic():
            populate(ratio)
        cache.delete('forum-sidebar')
        self.stdout.write(self.style.SUCCESS(
            f'Добавлено: {ratio} пользователей, {10 * ratio} вопросов, '
            f'{100 * ratio} ответов, {ratio} тегов, {200 * ratio} оценок.',
        ))
