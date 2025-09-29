from django.urls import path
from .views import RegisterDeviceView, PendingNotificationsView, AcknowledgeNotificationView

app_name = 'notifications'

urlpatterns = [
    path('register-device/', RegisterDeviceView.as_view(), name='register-device'),
    path('pending/', PendingNotificationsView.as_view(), name='pending'),
    path('ack/', AcknowledgeNotificationView.as_view(), name='ack'),
]

