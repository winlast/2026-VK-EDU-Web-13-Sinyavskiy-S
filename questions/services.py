from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum

from .models import Answer, Question


@transaction.atomic
def set_vote(model, target_field, item_id, user, value):
    # Блокировка цели сериализует изменение голосов и расчёт итоговой оценки.
    target = model._meta.get_field(target_field).related_model
    target.objects.select_for_update().only('pk').get(pk=item_id)
    votes = model.objects.filter(**{f'{target_field}_id': item_id})
    personal_vote = votes.filter(user=user)
    if value == 0:
        personal_vote.delete()
    else:
        personal_vote.update_or_create(user=user, defaults={f'{target_field}_id': item_id, 'value': value})
    return votes.aggregate(rating=Sum('value', default=0))['rating']


@transaction.atomic
def mark_correct(question_id, answer_id, user, correct):
    question = Question.objects.select_for_update().only('author').get(pk=question_id)
    if question.author_id != user.pk:
        raise PermissionDenied
    answer = question.answers.only('is_correct').get(pk=answer_id)
    if correct:
        question.answers.filter(is_correct=True).exclude(pk=answer.pk).update(is_correct=False)
    if answer.is_correct != correct:
        Answer.objects.filter(pk=answer.pk).update(is_correct=correct)
    return question.answers.filter(is_correct=True).values_list('pk', flat=True).first()
