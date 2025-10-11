from django.contrib.auth.hashers import make_password
from .models import MinhaEmpresa

class EmpresaAuthService:
    def gerar_tokens_para_empresa(self, empresa):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken()
        refresh['emp_uuid'] = str(empresa.uuid)
        refresh['emp_cnpj'] = empresa.cnpj
        access = refresh.access_token
        access['emp_uuid'] = str(empresa.uuid)
        access['emp_cnpj'] = empresa.cnpj
        return {
            'refresh': str(refresh),
            'access': str(access),
        }

    def criar_empresa_com_senha(self, cnpj: str, senha: str, nome: str) -> MinhaEmpresa:
        empresa, created = MinhaEmpresa.objects.get_or_create(
            cnpj=cnpj,
            defaults={'nome': nome}
        )
        empresa.senha_hash = make_password(senha)
        empresa.save(update_fields=['senha_hash'])
        return empresa