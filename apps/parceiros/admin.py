from django.contrib import admin
from .models import Parceiro


@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "tipo_display")
    search_fields = ("nome", "cnpj")
    list_filter = ("clf_tipo",)

    def tipo_display(self, obj: Parceiro):
        # Mostra tipo/código do classificador associado ao parceiro
        try:
            return f"{obj.clf_tipo.tipo}:{obj.clf_tipo.codigo}"
        except Exception:
            return str(getattr(obj, "clf_tipo", "-"))

    tipo_display.short_description = "Tipo"
    tipo_display.admin_order_field = "clf_tipo"
