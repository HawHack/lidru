from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import Coalesce

from users.models import User
from events.models import Event, EventParticipation


def get_latest_events(limit=6):
    return Event.objects.select_related('organizer').order_by('-created_at')[:limit]


def get_popular_directions():
    return list(
        Event.objects
        .values('direction')
        .annotate(total=Count('id'))
        .order_by('-total')
    )


def get_rating_chart_data(user):
    """Накопительный график баллов для авторизованного пользователя."""
    if not user.is_authenticated:
        return [], []

    participations = (
        EventParticipation.objects
        .filter(participant=user, status='confirmed')
        .select_related('event')
        .order_by('confirmed_at', 'created_at')
    )

    labels, data = [], []
    total = 0
    for p in participations:
        total += p.earned_points
        dt = p.confirmed_at or p.created_at
        labels.append(dt.strftime('%d.%m.%Y'))
        data.append(total)

    return labels, data


def get_filtered_candidates(filters):
    """
    Возвращает QuerySet участников с аннотированными rating / events_count / avg_score.
    Один SQL-запрос вместо N+1.
    """
    qs = User.objects.filter(role='participant')

    if filters.get('age_min'):
        qs = qs.filter(age__gte=filters['age_min'])
    if filters.get('age_max'):
        qs = qs.filter(age__lte=filters['age_max'])
    if filters.get('city'):
        qs = qs.filter(city__icontains=filters['city'])
    if filters.get('direction'):
        qs = qs.filter(direction=filters['direction'])

    qs = qs.annotate(
        rating=Coalesce(
            Sum(
                'event_participations__earned_points',
                filter=Q(event_participations__status='confirmed'),
            ),
            0,
        ),
        events_count=Count(
            'event_participations',
            filter=Q(event_participations__status='confirmed'),
        ),
        avg_score=Coalesce(
            Avg(
                'event_participations__earned_points',
                filter=Q(event_participations__status='confirmed'),
            ),
            0.0,
        ),
    )

    if filters.get('min_rating'):
        qs = qs.filter(rating__gte=int(filters['min_rating']))
    if filters.get('min_events'):
        qs = qs.filter(events_count__gte=int(filters['min_events']))

    return qs.order_by('-rating')


def get_candidate_stats(user):
    """Статистика одного кандидата для отчёта."""
    confirmed = EventParticipation.objects.filter(
        participant=user, status='confirmed',
    )
    agg = confirmed.aggregate(
        total_rating=Coalesce(Sum('earned_points'), 0),
        events_count=Count('id'),
        avg_score=Coalesce(Avg('earned_points'), 0.0),
    )
    agg['avg_score'] = round(agg['avg_score'], 1)
    return agg