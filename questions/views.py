from django.http import Http404
from django.shortcuts import render

from . import data
from .utils import paginate


def index(request):
    page = paginate(data.get_new_questions(), request)
    return render(request, 'questions/index.html', {'page': page})


def hot(request):
    page = paginate(data.get_hot_questions(), request)
    return render(request, 'questions/hot.html', {'page': page})


def tag(request, tag_name):
    questions = data.get_questions_by_tag(tag_name)
    if not questions:
        raise Http404('Тег не найден')

    page = paginate(questions, request)
    return render(request, 'questions/tag.html', {'page': page, 'tag': tag_name})


def question(request, question_id):
    item = data.get_question(question_id)
    if item is None:
        raise Http404('Вопрос не найден')

    page = paginate(data.get_answers(item), request, per_page=5)
    return render(request, 'questions/question.html', {'question': item, 'page': page})


def ask(request):
    return render(request, 'questions/ask.html')
