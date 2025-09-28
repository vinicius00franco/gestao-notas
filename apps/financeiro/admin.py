from django.contrib import admin
from .models import LancamentoFinanceiro


@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ("descricao", "valor", "data_vencimento", "data_pagamento")
    # list_filter pode ser refeito com clf_tipo__codigo / clf_status__codigo
    list_filter = ("clf_tipo", "clf_status")
    search_fields = ("descricao",)
