from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from .managers import AnswerQuerySet, QuestionQuerySet, TagQuerySet


class Tag(models.Model):
    name = models.CharField(
        'название', max_length=50, unique=True,
        validators=[RegexValidator(r'^[\w+#.-]+\Z', 'Используйте буквы, цифры и символы _ + # . -')],
    )
    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ['name']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', args=[self.name])


class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='questions', verbose_name='автор',
    )
    title = models.CharField('заголовок', max_length=120)
    text = models.TextField('текст', max_length=3000)
    created_at = models.DateTimeField('создан', auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True, verbose_name='теги')
    objects = QuestionQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=['-created_at', '-id'])]
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question', args=[self.pk])


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers', verbose_name='вопрос',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='answers', verbose_name='автор',
    )
    text = models.TextField('текст', max_length=3000)
    created_at = models.DateTimeField('создан', auto_now_add=True, db_index=True)
    is_correct = models.BooleanField('правильный ответ', default=False)
    objects = AnswerQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question'], condition=models.Q(is_correct=True),
                name='one_correct_answer_per_question',
            ),
        ]
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'

    def __str__(self):
        return self.text[:80]


class Vote(models.Model):
    class Value(models.IntegerChoices):
        UP = 1, 'Нравится'
        DOWN = -1, 'Не нравится'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='пользователь',
    )
    value = models.SmallIntegerField('оценка', choices=Value.choices)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(condition=models.Q(value__in=[-1, 1]), name='%(class)s_valid_value'),
        ]


class QuestionLike(Vote):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='вопрос')

    class Meta(Vote.Meta):
        constraints = Vote.Meta.constraints + [
            models.UniqueConstraint(fields=['question', 'user'], name='one_vote_per_question'),
        ]
        verbose_name = 'оценка вопроса'
        verbose_name_plural = 'оценки вопросов'


class AnswerLike(Vote):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='ответ')

    class Meta(Vote.Meta):
        constraints = Vote.Meta.constraints + [
            models.UniqueConstraint(fields=['answer', 'user'], name='one_vote_per_answer'),
        ]
        verbose_name = 'оценка ответа'
        verbose_name_plural = 'оценки ответов'
