from django.shortcuts import render

from users.models import User
from .services import get_leaderboard


def leaderboard_view(request):
    direction = request.GET.get('direction')
    city = request.GET.get('city')

    context = {
        'leaderboard': get_leaderboard(direction=direction, city=city),
        'selected_direction': direction,
        'selected_city': city,
        'direction_choices': User.DIRECTION_CHOICES,
    }
    return render(request, 'ratings/leaderboard.html', context)