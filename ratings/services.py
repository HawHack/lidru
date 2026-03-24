from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import Coalesce

from users.models import User
from events.models import EventParticipation


LEVELS = [
    ('Новичок', 0),
    ('Активист', 100),
    ('Кадровый резерв', 250),
    ('Лидер', 500),
]


def get_user_rating(user):
    if not user.is_authenticated:
        return 0
    result = EventParticipation.objects.filter(
        participant=user, status='confirmed',
    ).aggregate(total=Sum('earned_points'))
    return result['total'] or 0


def get_user_confirmed_events_count(user):
    if not user.is_authenticated:
        return 0
    return EventParticipation.objects.filter(
        participant=user, status='confirmed',
    ).count()


def _participant_with_stats():
    """Базовый queryset участников с аннотированной статистикой."""
    return User.objects.filter(role='participant').annotate(
        rating=Coalesce(
            Sum(
                'event_participations__earned_points',
                filter=Q(event_participations__status='confirmed'),
            ),
            0,
        ),
        confirmed_events_count=Count(
            'event_participations',
            filter=Q(event_participations__status='confirmed'),
        ),
    )


def get_leaderboard(direction=None, city=None, limit=100):
    qs = _participant_with_stats()
    if direction:
        qs = qs.filter(direction=direction)
    if city:
        qs = qs.filter(city__icontains=city)
    return qs.order_by('-rating')[:limit]


def get_user_rank(user):
    if user.role != 'participant':
        return None
    user_rating = get_user_rating(user)
    rank = (
        _participant_with_stats()
        .filter(rating__gt=user_rating)
        .count()
        + 1
    )
    return rank


def get_user_portfolio(user):
    return (
        EventParticipation.objects
        .filter(participant=user, status='confirmed')
        .select_related('event', 'event__organizer')
        .order_by('-confirmed_at', '-created_at')
    )


def get_level_info(points):
    current_level = LEVELS[0][0]
    next_level = None
    points_to_next = 0

    for i, (name, min_pts) in enumerate(LEVELS):
        if points >= min_pts:
            current_level = name
            if i + 1 < len(LEVELS):
                next_level = LEVELS[i + 1][0]
                points_to_next = max(0, LEVELS[i + 1][1] - points)
            else:
                next_level = None
                points_to_next = 0

    return {
        'current_level': current_level,
        'next_level': next_level,
        'points_to_next': points_to_next,
    }