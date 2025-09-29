from typing import Optional, Tuple
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework_simplejwt.backends import TokenBackend
from apps.empresa.models import MinhaEmpresa


class EmpresaPrincipal:
    """Lightweight principal representing an authenticated company.

    Behaves like a Django user for permission checks (is_authenticated = True).
    """

    def __init__(self, empresa: MinhaEmpresa):
        self.empresa = empresa
        self.is_authenticated = True

    @property
    def minhaempresa(self):
        return self.empresa


class EmpresaJWTAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request: Request) -> Optional[Tuple[EmpresaPrincipal, str]]:
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(_('Invalid Authorization header. No credentials provided.'))
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed(_('Invalid Authorization header.'))

        token = auth[1].decode('utf-8')
        try:
            backend = TokenBackend(algorithm='HS256')
            payload = backend.decode(token, verify=True)
        except Exception:
            # Not our token format; let other authenticators try
            return None

        emp_uuid = payload.get('emp_uuid')
        emp_cnpj = payload.get('emp_cnpj')
        if not emp_uuid or not emp_cnpj:
            return None

        try:
            empresa = MinhaEmpresa.objects.get(uuid=emp_uuid, cnpj=emp_cnpj)
        except MinhaEmpresa.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Empresa inválida'))

        principal = EmpresaPrincipal(empresa)
        return (principal, token)
