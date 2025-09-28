from django.urls import path
from .views import DashboardStatsView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
