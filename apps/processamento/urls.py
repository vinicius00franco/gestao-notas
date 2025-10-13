from django.urls import path
from .views import ProcessarNotaFiscalView, JobStatusView
from .views import JobListView, JobPendentesView, JobConcluidosView, JobErrosView

urlpatterns = [
    path('processar-nota/', ProcessarNotaFiscalView.as_view(), name='processar-nota'),
    path('jobs/', JobListView.as_view(), name='jobs-list'),
    path('jobs/pendentes/', JobPendentesView.as_view(), name='jobs-pendentes'),
    path('jobs/concluidos/', JobConcluidosView.as_view(), name='jobs-concluidos'),
    path('jobs/erros/', JobErrosView.as_view(), name='jobs-erros'),
    path('jobs/<uuid:uuid>/', JobStatusView.as_view(), name='job-status'),
]
