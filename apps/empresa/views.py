from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import EmpresaLoginSerializer, EmpresaSenhaSetupSerializer


class EmpresaLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = EmpresaLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        empresa = ser.validated_data['empresa']
        # Gera JWT para este "usuário de empresa". Como não é um User do Django,
        # podemos embutir claims extras no token.
        refresh = RefreshToken.for_user(request.user) if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False) else RefreshToken()
        # Colocar claims customizados no refresh e também no access
        refresh['emp_uuid'] = str(empresa.uuid)
        refresh['emp_cnpj'] = empresa.cnpj
        access = refresh.access_token
        access['emp_uuid'] = str(empresa.uuid)
        access['emp_cnpj'] = empresa.cnpj

        return Response({
            'access': str(access),
            'refresh': str(refresh),
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
        empresa = ser.save()
        return Response({'ok': True, 'empresa': empresa.cnpj}, status=status.HTTP_201_CREATED)
