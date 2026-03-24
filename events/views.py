from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from users.models import User
from .forms import EventForm, OrganizerReviewForm
from .models import Event, EventParticipation, OrganizerReview
from .services import build_organizer_context


def event_list_view(request):
    events = Event.objects.select_related('organizer').order_by('date')

    direction = request.GET.get('direction')
    status = request.GET.get('status')

    if direction:
        events = events.filter(direction=direction)
    if status == 'upcoming':
        events = events.filter(date__gte=timezone.now())
    elif status == 'past':
        events = events.filter(date__lt=timezone.now())

    context = {
        'events': events,
        'selected_direction': direction,
        'selected_status': status,
        'direction_choices': Event.DIRECTION_CHOICES,
    }
    return render(request, 'events/event_list.html', context)


def event_detail_view(request, event_id):
    event = get_object_or_404(Event.objects.select_related('organizer'), id=event_id)

    participation = None
    checkin_url = None

    if request.user.is_authenticated and request.user.role == 'participant':
        participation = EventParticipation.objects.filter(
            event=event, participant=request.user,
        ).first()
        if participation:
            checkin_url = request.build_absolute_uri(
                f'/events/checkin/{participation.qr_token}/'
            )

    context = {
        'event': event,
        'participation': participation,
        'checkin_url': checkin_url,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def event_create_view(request):
    if request.user.role != 'organizer':
        messages.error(request, 'Только организатор может создавать мероприятия.')
        return redirect('event_list')

    if not request.user.is_approved_organizer:
        messages.warning(request, 'Ваш аккаунт организатора еще не одобрен.')
        return redirect('event_list')

    form = EventForm(request.POST or None)
    if form.is_valid():
        event = form.save(commit=False)
        event.organizer = request.user
        event.save()
        messages.success(request, 'Мероприятие успешно создано.')
        return redirect('event_detail', event_id=event.id)

    return render(request, 'events/event_form.html', {
        'form': form,
        'page_title': 'Создать мероприятие',
    })


@login_required
def event_update_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user != event.organizer:
        messages.error(request, 'Вы не можете редактировать это мероприятие.')
        return redirect('event_detail', event_id=event.id)

    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, 'Мероприятие обновлено.')
        return redirect('event_detail', event_id=event.id)

    return render(request, 'events/event_form.html', {
        'form': form,
        'page_title': 'Редактировать мероприятие',
    })


@login_required
def register_for_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.role != 'participant':
        messages.error(request, 'Записываться на мероприятие могут только участники.')
        return redirect('event_detail', event_id=event.id)

    _, created = EventParticipation.objects.get_or_create(
        event=event,
        participant=request.user,
        defaults={'status': 'registered'},
    )
    if created:
        messages.success(request, 'Вы успешно записались на мероприятие.')
    else:
        messages.info(request, 'Вы уже записаны на это мероприятие.')

    return redirect('event_detail', event_id=event.id)


@login_required
def my_events_view(request):
    participations = (
        EventParticipation.objects
        .filter(participant=request.user)
        .select_related('event', 'event__organizer')
        .order_by('-created_at')
    )
    return render(request, 'events/my_events.html', {'participations': participations})


@login_required
def organizer_event_participants_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user != event.organizer:
        messages.error(request, 'Вы не можете просматривать участников этого мероприятия.')
        return redirect('event_detail', event_id=event.id)

    participations = (
        EventParticipation.objects
        .filter(event=event)
        .select_related('participant')
        .order_by('-created_at')
    )
    return render(request, 'events/event_participants.html', {
        'event': event,
        'participations': participations,
    })


@login_required
def confirm_participation_view(request, participation_id):
    participation = get_object_or_404(EventParticipation, id=participation_id)
    event = participation.event

    if request.user != event.organizer:
        messages.error(request, 'Только организатор может подтверждать участие.')
        return redirect('event_detail', event_id=event.id)

    if participation.status != 'confirmed':
        participation.status = 'confirmed'
        participation.earned_points = event.calculated_points()
        participation.confirmed_by = request.user
        participation.confirmed_at = timezone.now()
        participation.save()
        messages.success(request, 'Участие подтверждено, баллы начислены.')
    else:
        messages.info(request, 'Это участие уже подтверждено.')

    return redirect('organizer_event_participants', event_id=event.id)


@login_required
def checkin_by_qr_view(request, token):
    participation = get_object_or_404(EventParticipation, qr_token=token)

    if request.user.role != 'participant':
        messages.error(request, 'QR check-in доступен только участникам.')
        return redirect('event_detail', event_id=participation.event.id)

    if participation.participant != request.user:
        messages.error(request, 'Этот QR-код не принадлежит вашему участию.')
        return redirect('event_detail', event_id=participation.event.id)

    status_messages = {
        'registered': ('attended', 'Присутствие отмечено. Ожидайте подтверждения.'),
        'attended': (None, 'Вы уже отметили присутствие.'),
        'confirmed': (None, 'Ваше участие уже подтверждено.'),
    }
    new_status, msg = status_messages.get(participation.status, (None, ''))

    if new_status:
        participation.status = new_status
        participation.save()
        messages.success(request, msg)
    else:
        messages.info(request, msg)

    return redirect('event_detail', event_id=participation.event.id)


# ---------- Organizer profile ----------

def organizer_detail_view(request, organizer_id):
    organizer = get_object_or_404(User, id=organizer_id, role='organizer')
    context = build_organizer_context(organizer, request.user)
    return render(request, 'events/organizer_detail.html', context)


@login_required
def add_organizer_review_view(request, organizer_id):
    organizer = get_object_or_404(User, id=organizer_id, role='organizer')

    if request.user.role != 'participant':
        messages.error(request, 'Отзывы могут оставлять только участники.')
        return redirect('organizer_detail', organizer_id=organizer.id)

    if organizer == request.user:
        messages.error(request, 'Нельзя оставить отзыв самому себе.')
        return redirect('organizer_detail', organizer_id=organizer.id)

    if OrganizerReview.objects.filter(organizer=organizer, participant=request.user).exists():
        messages.info(request, 'Вы уже оставляли отзыв этому организатору.')
        return redirect('organizer_detail', organizer_id=organizer.id)

    form = OrganizerReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.organizer = organizer
        review.participant = request.user
        review.save()
        messages.success(request, 'Отзыв успешно добавлен.')
        return redirect('organizer_detail', organizer_id=organizer.id)

    # Контекст строится сервисом — ноль дублирования
    context = build_organizer_context(organizer, request.user)
    context.update({
        'review_form': form,
        'show_review_form': True,
        'can_leave_review': True,
    })
    return render(request, 'events/organizer_detail.html', context)