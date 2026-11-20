from functools import wraps

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import JsonResponse

from .forms import CorrectAnswerForm, VoteForm
from .models import AnswerLike, QuestionLike
from .services import mark_correct, set_vote


def ajax_form(form_class):
    def decorate(view):
        @wraps(view)
        def handle(request, *args, **kwargs):
            if request.method != 'POST':
                return JsonResponse({'error': 'Ожидается POST.'}, status=405, headers={'Allow': 'POST'})
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Войдите, чтобы продолжить.'}, status=401)
            form = form_class(request.POST)
            if not form.is_valid():
                return JsonResponse({'error': 'Неверные данные.', 'fields': form.errors}, status=400)
            try:
                return JsonResponse(view(request.user, form.cleaned_data, *args, **kwargs))
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Запись не найдена.'}, status=404)
            except PermissionDenied:
                return JsonResponse({'error': 'Отметку может изменять только автор вопроса.'}, status=403)

        return handle

    return decorate


@ajax_form(VoteForm)
def vote_question(user, data, question_id):
    value = data['value']
    rating = set_vote(QuestionLike, 'question', question_id, user, value)
    return {'rating': rating, 'value': value}


@ajax_form(VoteForm)
def vote_answer(user, data, answer_id):
    value = data['value']
    rating = set_vote(AnswerLike, 'answer', answer_id, user, value)
    return {'rating': rating, 'value': value}


@ajax_form(CorrectAnswerForm)
def correct_answer(user, data, question_id, answer_id):
    return {'correct_answer_id': mark_correct(question_id, answer_id, user, data['correct'])}
