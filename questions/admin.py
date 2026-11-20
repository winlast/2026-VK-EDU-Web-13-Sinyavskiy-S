from django.contrib import admin
from django.db.models import Count

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('author', 'text', 'is_correct')
    autocomplete_fields = ('author',)
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'text', 'author__username')
    list_select_related = ('author',)
    autocomplete_fields = ('author', 'tags')
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('preview', 'question', 'author', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('text', 'question__title', 'author__username')
    list_select_related = ('question', 'author')
    autocomplete_fields = ('question', 'author')

    @admin.display(description='Текст')
    def preview(self, answer):
        return str(answer)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'usage')
    search_fields = ('name',)
    list_filter = (('questions', admin.EmptyFieldListFilter),)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(question_count=Count('questions'))

    @admin.display(ordering='question_count', description='Вопросов')
    def usage(self, tag):
        return tag.question_count


class LikeAdmin(admin.ModelAdmin):
    list_filter = ('value',)


@admin.register(QuestionLike)
class QuestionLikeAdmin(LikeAdmin):
    list_display = ('question', 'user', 'value')
    search_fields = ('question__title', 'user__username')
    list_select_related = ('question', 'user')
    autocomplete_fields = ('question', 'user')


@admin.register(AnswerLike)
class AnswerLikeAdmin(LikeAdmin):
    list_display = ('answer', 'user', 'value')
    search_fields = ('answer__text', 'user__username')
    list_select_related = ('answer', 'user')
    autocomplete_fields = ('answer', 'user')
