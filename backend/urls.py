from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health import healthz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', healthz, name='healthz'),
    path('api/', include('apps.processamento.urls')),
    path('api/', include('apps.financeiro.urls')),
    path('api/', include('apps.dashboard.urls')),
    path('api/', include('apps.empresa.urls')),
    path('api/', include('apps.notas.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

# Servir arquivos de media em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
