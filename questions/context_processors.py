from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from .models import Answer, Question, Tag


def sidebar_data():
    since = timezone.now() - timedelta(days=7)
    scores = []
    for model in (Question, Answer):
        scores.extend(
            model.objects.filter(created_at__gte=since).with_rating()
            .order_by('-rating', '-created_at', '-pk').values_list('author_id', 'rating')[:30]
        )
    ranked_ids = list(dict.fromkeys(pk for pk, _ in sorted(scores, key=lambda row: -row[1])))[:10]
    members = get_user_model().objects.select_related('profile').in_bulk(ranked_ids)
    return {
        'popular_tags': list(Tag.objects.popular()[:20]),
        'best_members': [members[pk] for pk in ranked_ids if pk in members],
    }


def sidebar(request):
    return cache.get_or_set('forum-sidebar', sidebar_data, timeout=60)
