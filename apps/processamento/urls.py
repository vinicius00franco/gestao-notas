from django.urls import path
from .views import ProcessarNotaFiscalView, JobStatusView

urlpatterns = [
    path('processar-nota/', ProcessarNotaFiscalView.as_view(), name='processar-nota'),
    path('jobs/<int:id>/', JobStatusView.as_view(), name='job-status'),
]
