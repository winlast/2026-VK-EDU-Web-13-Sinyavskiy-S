from django.shortcuts import get_object_or_404, render

from .models import Answer, Question, Tag
from .utils import ANSWERS_PER_PAGE, QUESTIONS_PER_PAGE, paginate


def listing(request, template, questions, **context):
    search = request.GET.get('q', '').strip()[:100]
    page = paginate(questions.search(search), request, per_page=QUESTIONS_PER_PAGE)
    return render(request, template, {'page': page, 'search': search, **context})


def index(request):
    return listing(request, 'questions/index.html', Question.objects.newest())


def hot(request):
    return listing(request, 'questions/hot.html', Question.objects.hottest())


def tag(request, tag_name):
    item = get_object_or_404(Tag, name=tag_name)
    return listing(request, 'questions/tag.html', Question.objects.by_tag(item), tag=item)


def question(request, question_id):
    item = get_object_or_404(Question.objects.with_cards(), pk=question_id)
    page = paginate(Answer.objects.for_question(item), request, per_page=ANSWERS_PER_PAGE)
    return render(request, 'questions/question.html', {'question': item, 'page': page})


def ask(request):
    return render(request, 'questions/ask.html')
