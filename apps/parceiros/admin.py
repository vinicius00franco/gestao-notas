from django.contrib import admin
from .models import Parceiro

@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "tipo")
    search_fields = ("nome", "cnpj")
    list_filter = ("tipo",)
