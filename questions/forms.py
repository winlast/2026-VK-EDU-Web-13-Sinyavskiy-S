from django import forms
from django.db import transaction

from core.forms import BootstrapFields

from .models import Answer, Question, Tag, Vote


class QuestionForm(BootstrapFields, forms.ModelForm):
    tags = forms.CharField(
        label='Теги', required=False, max_length=152,
        help_text='Укажите до трёх тегов через запятую. Например: python, иу5.',
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        help_texts = {'title': 'До 120 символов.', 'text': 'До 3000 символов.'}
        widgets = {'text': forms.Textarea(attrs={'rows': 6})}

    def __init__(self, *args, author, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.author = author

    def clean_tags(self):
        names = list(dict.fromkeys(
            part.strip().casefold() for part in self.cleaned_data['tags'].split(',') if part.strip()
        ))
        if len(names) > 3:
            raise forms.ValidationError('Укажите не больше трёх тегов.')
        field = Tag._meta.get_field('name')
        for name in names:
            if name in {'.', '..'}:
                raise forms.ValidationError('Тег должен содержать название.')
            field.clean(name, None)
        return names

    @transaction.atomic
    def save(self, commit=True):
        question = super().save(commit=False)

        def save_tags():
            question.tags.set([Tag.objects.get_or_create(name=name)[0] for name in self.cleaned_data['tags']])

        if commit:
            question.save()
            save_tags()
        else:
            self.save_m2m = save_tags
        return question


class AnswerForm(BootstrapFields, forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        help_texts = {'text': 'До 3000 символов.'}
        widgets = {'text': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, author, question, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.author = author
        self.instance.question = question


class VoteForm(forms.Form):
    value = forms.TypedChoiceField(
        choices=[(0, 'Снять оценку'), *Vote.Value.choices], coerce=int,
    )


class CorrectAnswerForm(forms.Form):
    correct = forms.TypedChoiceField(
        choices=[('true', 'Отметить'), ('false', 'Снять отметку')], coerce=lambda value: value == 'true',
    )
