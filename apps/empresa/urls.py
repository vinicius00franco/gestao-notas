from django.urls import path
from .views import EmpresaLoginView, EmpresaSenhaSetupView

app_name = 'empresa'

urlpatterns = [
    path('auth/login/', EmpresaLoginView.as_view(), name='empresa-login'),
    path('auth/setup-senha/', EmpresaSenhaSetupView.as_view(), name='empresa-setup-senha'),
]
