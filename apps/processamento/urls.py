from django.urls import path
from .views import ProcessarNotaFiscalView, JobStatusView
from .views import JobListView

urlpatterns = [
    path('processar-nota/', ProcessarNotaFiscalView.as_view(), name='processar-nota'),
    path('jobs/', JobListView.as_view(), name='jobs-list'),
    path('jobs/<uuid:uuid>/', JobStatusView.as_view(), name='job-status'),
]
