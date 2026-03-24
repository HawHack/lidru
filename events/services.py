from django.db.models import Avg

from events.models import Event, OrganizerReview


def build_organizer_context(organizer, request_user=None):
    """
    Собирает полный контекст для страницы организатора.
    Переиспользуется в detail и review views — ноль дублирования.
    """
    events = Event.objects.filter(organizer=organizer).order_by('-date')
    reviews = (
        OrganizerReview.objects
        .filter(organizer=organizer)
        .select_related('participant')
        .order_by('-created_at')
    )

    trust_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    bonus_list = list(
        events.exclude(bonus_text='')
        .values_list('bonus_text', flat=True)
        .distinct()
    )

    existing_review = None
    can_leave_review = False

    if (
        request_user
        and request_user.is_authenticated
        and request_user.role == 'participant'
    ):
        existing_review = OrganizerReview.objects.filter(
            organizer=organizer, participant=request_user,
        ).first()
        if organizer != request_user and not existing_review:
            can_leave_review = True

    return {
        'organizer': organizer,
        'events': events,
        'events_count': events.count(),
        'reviews': reviews,
        'reviews_count': reviews.count(),
        'trust_rating': trust_rating,
        'bonus_list': bonus_list,
        'existing_review': existing_review,
        'can_leave_review': can_leave_review,
    }