from rest_framework import serializers
from .models import Classificador

class ClassificadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classificador
        fields = ('uuid', 'tipo', 'codigo', 'descricao')