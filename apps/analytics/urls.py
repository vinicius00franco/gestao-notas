from django.urls import path
from .views import MobileMetricsView

urlpatterns = [
    path('mobile-metrics/', MobileMetricsView.as_view(), name='mobile-metrics'),
]