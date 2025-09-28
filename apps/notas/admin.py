from django.contrib import admin
from .models import NotaFiscal

@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ("numero", "parceiro", "data_emissao", "valor_total")
    search_fields = ("numero",)
    list_filter = ("data_emissao",)
