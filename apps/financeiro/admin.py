from django.contrib import admin
from .models import LancamentoFinanceiro

@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ("descricao", "tipo", "status", "valor", "data_vencimento")
    list_filter = ("tipo", "status")
    search_fields = ("descricao",)
