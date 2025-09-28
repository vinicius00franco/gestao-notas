from django.urls import path
from .views import ContasAPagarListView, ContasAReceberListView

urlpatterns = [
    path('contas-a-pagar/', ContasAPagarListView.as_view(), name='contas-a-pagar'),
    path('contas-a-receber/', ContasAReceberListView.as_view(), name='contas-a-receber'),
]
