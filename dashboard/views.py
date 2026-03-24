import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from users.models import User
from events.models import EventParticipation
from .services import (
    get_latest_events,
    get_popular_directions,
    get_rating_chart_data,
    get_filtered_candidates,
    get_candidate_stats,
)


def main_view(request):
    return render(request, 'main.html')


def home_view(request):
    labels, data = get_rating_chart_data(request.user)

    context = {
        'latest_events': get_latest_events(),
        'popular_directions': get_popular_directions(),
        'chart_labels_json': json.dumps(labels, ensure_ascii=False),
        'chart_data_json': json.dumps(data),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def inspector_dashboard_view(request):
    if request.user.role != 'observer':
        messages.error(request, 'Доступ разрешен только кадровой службе.')
        return redirect('home')

    filters = {
        'age_min': request.GET.get('age_min'),
        'age_max': request.GET.get('age_max'),
        'city': request.GET.get('city'),
        'direction': request.GET.get('direction'),
        'min_rating': request.GET.get('min_rating'),
        'min_events': request.GET.get('min_events'),
    }

    context = {
        'candidates': get_filtered_candidates(filters),
        'direction_choices': User.DIRECTION_CHOICES,
        'filters': {k: v or '' for k, v in filters.items()},
    }
    return render(request, 'dashboard/inspector_dashboard.html', context)


@login_required
def candidate_report_view(request, user_id):
    if request.user.role != 'observer':
        messages.error(request, 'Доступ разрешен только кадровой службе.')
        return redirect('home')

    candidate = get_object_or_404(User, id=user_id, role='participant')
    stats = get_candidate_stats(candidate)

    confirmed_participations = (
        EventParticipation.objects
        .filter(participant=candidate, status='confirmed')
        .select_related('event', 'event__organizer')
        .order_by('-confirmed_at', '-created_at')
    )

    context = {
        'candidate': candidate,
        'confirmed_participations': confirmed_participations,
        **stats,
    }
    return render(request, 'dashboard/candidate_report.html', context)