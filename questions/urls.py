from django.urls import path

from . import ajax, views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/vote/', ajax.vote_question, name='vote-question'),
    path('answer/<int:answer_id>/vote/', ajax.vote_answer, name='vote-answer'),
    path(
        'question/<int:question_id>/answer/<int:answer_id>/correct/',
        ajax.correct_answer, name='correct-answer',
    ),
]
