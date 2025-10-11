from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import EmpresaLoginSerializer, EmpresaSenhaSetupSerializer
from .services import EmpresaAuthService
from .models import EmpresaNaoClassificada
from rest_framework import generics

class EmpresaLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = EmpresaLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        empresa = ser.validated_data['empresa']

        service = EmpresaAuthService()
        tokens = service.gerar_tokens_para_empresa(empresa)

        return Response({
            **tokens,
            'empresa': {
                'uuid': str(empresa.uuid),
                'cnpj': empresa.cnpj,
                'nome': empresa.nome,
            }
        })

class EmpresaSenhaSetupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = EmpresaSenhaSetupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        validated_data = ser.validated_data

        service = EmpresaAuthService()
        empresa = service.criar_empresa_com_senha(
            cnpj=validated_data['cnpj'],
            senha=validated_data['senha'],
            nome=validated_data.get('nome', '')
        )

        return Response({'ok': True, 'empresa': empresa.cnpj}, status=status.HTTP_201_CREATED)

class EmpresaNaoClassificadaView(generics.ListAPIView):
    queryset = EmpresaNaoClassificada.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        # Simples serializer inline para listagem
        from rest_framework import serializers
        class EmpresaNaoClassificadaSerializer(serializers.ModelSerializer):
            class Meta:
                model = EmpresaNaoClassificada
                fields = '__all__'
        return EmpresaNaoClassificadaSerializer
