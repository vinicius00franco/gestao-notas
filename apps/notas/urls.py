from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotaFiscalViewSet

router = DefaultRouter()
router.register(r'notas-fiscais', NotaFiscalViewSet, basename='notafiscal')

urlpatterns = [
    path('', include(router.urls)),
]