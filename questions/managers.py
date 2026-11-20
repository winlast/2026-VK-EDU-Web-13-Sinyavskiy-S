from django.db import models
from django.db.models import Count, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce


def related_total(model, field, aggregate):
    totals = (
        model.objects.filter(**{field: OuterRef('pk')}).order_by()
        .values(field).annotate(total=aggregate).values('total')
    )
    return Coalesce(Subquery(totals), 0)


def with_personal_vote(queryset, model, field, user):
    if not user.is_authenticated:
        return queryset
    vote = model.objects.filter(**{field: OuterRef('pk')}, user=user).values('value')
    return queryset.annotate(user_vote=Coalesce(Subquery(vote), models.Value(0), output_field=models.IntegerField()))


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(usage=Count('questions')).filter(usage__gt=0).order_by('-usage', 'name')


class QuestionQuerySet(models.QuerySet):
    def with_user_vote(self, user):
        from .models import QuestionLike

        return with_personal_vote(self, QuestionLike, 'question', user)

    def with_rating(self):
        from .models import QuestionLike

        return self.annotate(rating=related_total(QuestionLike, 'question', Sum('value')))

    def with_cards(self):
        from .models import Answer

        return (
            self.with_rating().select_related('author__profile').prefetch_related('tags')
            .annotate(answers_count=related_total(Answer, 'question', Count('pk')))
        )

    def newest(self):
        return self.with_cards().order_by('-created_at', '-pk')

    def hottest(self):
        return self.with_cards().order_by('-rating', '-created_at', '-pk')

    def by_tag(self, tag):
        return self.filter(tags=tag).hottest()

    def search(self, term):
        if not term:
            return self
        return self.filter(models.Q(title__icontains=term) | models.Q(text__icontains=term))


class AnswerQuerySet(models.QuerySet):
    def with_user_vote(self, user):
        from .models import AnswerLike

        return with_personal_vote(self, AnswerLike, 'answer', user)

    def with_rating(self):
        from .models import AnswerLike

        return self.annotate(rating=related_total(AnswerLike, 'answer', Sum('value')))

    def position(self, answer):
        rating = self.with_rating().filter(pk=answer.pk).values_list('rating', flat=True).get()
        before = (
            models.Q(rating__gt=rating)
            | models.Q(rating=rating, created_at__gt=answer.created_at)
            | models.Q(rating=rating, created_at=answer.created_at, pk__gt=answer.pk)
        )
        return self.with_rating().filter(question_id=answer.question_id).filter(before).count()

    def for_question(self, question):
        return (
            self.filter(question=question).select_related('author__profile').with_rating()
            .order_by('-rating', '-created_at', '-pk')
        )
