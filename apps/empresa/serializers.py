from rest_framework import serializers
from django.contrib.auth.hashers import check_password, make_password
from .models import MinhaEmpresa


class EmpresaLoginSerializer(serializers.Serializer):
    cnpj = serializers.CharField()
    senha = serializers.CharField(write_only=True)

    def validate(self, attrs):
        cnpj = attrs.get('cnpj')
        senha = attrs.get('senha')
        try:
            empresa = MinhaEmpresa.objects.get(cnpj=cnpj)
        except MinhaEmpresa.DoesNotExist:
            raise serializers.ValidationError('CNPJ ou senha inválidos')

        if not empresa.senha_hash:
            raise serializers.ValidationError('Empresa sem senha definida')

        if not check_password(senha, empresa.senha_hash):
            raise serializers.ValidationError('CNPJ ou senha inválidos')

        attrs['empresa'] = empresa
        return attrs


class EmpresaSenhaSetupSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = MinhaEmpresa
        fields = ['cnpj', 'senha']
        # Remove validação de unicidade do CNPJ porque usamos get_or_create
        extra_kwargs = {
            'cnpj': {'validators': []},
        }

    def create(self, validated_data):
        cnpj = validated_data['cnpj']
        senha = validated_data['senha']
        empresa, _ = MinhaEmpresa.objects.get_or_create(cnpj=cnpj)
        empresa.senha_hash = make_password(senha)
        empresa.save(update_fields=['senha_hash'])
        return empresa
