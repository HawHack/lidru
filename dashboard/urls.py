from django.urls import path
from .views import main_view, home_view, inspector_dashboard_view, candidate_report_view

urlpatterns = [
    path('', main_view, name='main'),
    path('dashboard/', home_view, name='home'),
    path('inspector/', inspector_dashboard_view, name='inspector_dashboard'),
    path('inspector/candidate/<int:user_id>/', candidate_report_view, name='candidate_report'),
]