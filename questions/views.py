from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import AnswerForm, QuestionForm
from .models import Answer, Question, Tag
from .utils import ANSWERS_PER_PAGE, QUESTIONS_PER_PAGE, paginate


def listing(request, template, questions, **context):
    search = request.GET.get('q', '').strip()[:100]
    page = paginate(questions.search(search).with_user_vote(request.user), request, per_page=QUESTIONS_PER_PAGE)
    return render(request, template, {'page': page, 'search': search, **context})


def index(request):
    return listing(request, 'questions/index.html', Question.objects.newest())


def hot(request):
    return listing(request, 'questions/hot.html', Question.objects.hottest())


def tag(request, tag_name):
    item = get_object_or_404(Tag, name=tag_name)
    return listing(request, 'questions/tag.html', Question.objects.by_tag(item), tag=item)


def question_page(request, item, form=None):
    answers = Answer.objects.for_question(item).with_user_vote(request.user)
    page = paginate(answers, request, per_page=ANSWERS_PER_PAGE)
    return render(request, 'questions/question.html', {'question': item, 'page': page, 'form': form})


@login_required
@require_http_methods(['POST'])
def add_answer(request, item):
    form = AnswerForm(request.POST, author=request.user, question=item)
    if form.is_valid():
        answer = form.save()
        messages.success(request, 'Ответ добавлен.')
        return redirect(answer.get_absolute_url())
    return question_page(request, item, form)


@require_http_methods(['GET', 'HEAD', 'POST'])
def question(request, question_id):
    if request.method == 'POST' and not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    item = get_object_or_404(Question.objects.with_cards().with_user_vote(request.user), pk=question_id)
    if request.method == 'POST':
        return add_answer(request, item)
    form = AnswerForm(author=request.user, question=item) if request.user.is_authenticated else None
    return question_page(request, item, form)


@login_required
@require_http_methods(['GET', 'HEAD', 'POST'])
def ask(request):
    form = QuestionForm(request.POST if request.method == 'POST' else None, author=request.user)
    if form.is_valid():
        item = form.save()
        messages.success(request, 'Вопрос опубликован.')
        return redirect(item)
    return render(request, 'questions/ask.html', {'form': form})
