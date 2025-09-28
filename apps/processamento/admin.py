from django.contrib import admin
from .models import JobProcessamento

@admin.register(JobProcessamento)
class JobProcessamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "dt_criacao", "dt_conclusao")
    list_filter = ("status",)
    search_fields = ("id",)
