from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import EmpresaLoginSerializer, EmpresaSenhaSetupSerializer
from .services import EmpresaAuthService

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
