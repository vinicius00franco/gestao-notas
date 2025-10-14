from django.urls import path
from .views import (
    ContasAPagarListView,
    ContasAReceberListView,
    CalendarResumoView,
    CalendarDiaDetalhesView,
)

urlpatterns = [
    path('contas-a-pagar/', ContasAPagarListView.as_view(), name='contas-a-pagar'),
    path('contas-a-receber/', ContasAReceberListView.as_view(), name='contas-a-receber'),
    # Calendar endpoints
    path('calendar-resumo/', CalendarResumoView.as_view(), name='calendar-resumo'),
    path('calendar-dia/', CalendarDiaDetalhesView.as_view(), name='calendar-dia-detalhes'),
]
