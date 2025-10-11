from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.empresa.models import MinhaEmpresa

class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.empresa_cnpj = '12.345.678/0001-99'
        self.empresa_senha = 'testpassword'

        # Cria a empresa
        self.empresa = MinhaEmpresa.objects.create(
            nome='Empresa de Teste',
            cnpj=self.empresa_cnpj
        )

        # Configura a senha usando o endpoint
        setup_url = reverse('empresa:empresa-setup-senha')
        response = self.client.post(setup_url, {
            'cnpj': self.empresa_cnpj,
            'senha': self.empresa_senha
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Realiza o login para obter o token
        login_url = reverse('empresa:empresa-login')
        response = self.client.post(login_url, {
            'cnpj': self.empresa_cnpj,
            'senha': self.empresa_senha
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Configura o token no cliente de teste
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')