"""
Testes para o app empresa.
Testa autenticação, setup de senha e login com JWT.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.empresa.models import MinhaEmpresa


class EmpresaSenhaSetupTestCase(APITestCase):
    """
    Testes para o endpoint de setup de senha da empresa.
    RF: Empresa deve poder configurar senha para autenticação.
    RN005: CNPJ deve ser único por empresa.
    """

    def test_criar_empresa_com_senha_sucesso(self):
        """Testa criação de empresa com senha com dados válidos."""
        url = reverse('empresa:empresa-setup-senha')
        data = {
            'cnpj': '12.345.678/0001-99',
            'senha': 'SenhaSegura123!@#'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ok'], True)
        self.assertEqual(response.data['empresa'], '12.345.678/0001-99')
        
        # Verifica que empresa foi criada no banco (será revertida pelo rollback)
        self.assertTrue(MinhaEmpresa.objects.filter(cnpj='12.345.678/0001-99').exists())
        
        # Verifica que senha foi hashada (não armazena em texto plano)
        empresa = MinhaEmpresa.objects.get(cnpj='12.345.678/0001-99')
        self.assertNotEqual(empresa.senha_hash, 'SenhaSegura123!@#')
        self.assertTrue(empresa.senha_hash.startswith('pbkdf2_sha256$'))

    def test_atualizar_senha_empresa_existente(self):
        """
        Testa atualização de senha para empresa já cadastrada.
        O serializer usa get_or_create, então sempre retorna 201 (created).
        """
        # Cria empresa sem senha
        empresa = MinhaEmpresa.objects.create(cnpj='98.765.432/0001-11')
        
        url = reverse('empresa:empresa-setup-senha')
        data = {
            'cnpj': '98.765.432/0001-11',
            'senha': 'NovaSenha456!@#'
        }

        response = self.client.post(url, data, format='json')

        # Endpoint sempre retorna 201, mesmo para update
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica que senha foi atualizada
        empresa.refresh_from_db()
        self.assertIsNotNone(empresa.senha_hash)
        self.assertTrue(empresa.senha_hash.startswith('pbkdf2_sha256$'))

    def test_criar_empresa_sem_cnpj(self):
        """Testa validação de CNPJ obrigatório."""
        url = reverse('empresa:empresa-setup-senha')
        data = {
            'senha': 'SenhaSegura123!@#'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_empresa_sem_senha(self):
        """Testa validação de senha obrigatória."""
        url = reverse('empresa:empresa-setup-senha')
        data = {
            'cnpj': '12.345.678/0001-99'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmpresaLoginTestCase(APITestCase):
    """
    Testes para o endpoint de login da empresa.
    RF: Empresa deve poder fazer login com CNPJ e senha.
    Retorna JWT com claims customizados (emp_uuid, emp_cnpj).
    RN012: APIs usam UUID, não IDs numéricos.
    """

    def setUp(self):
        """Cria empresa com senha para usar nos testes."""
        self.cnpj = '11.222.333/0001-44'
        self.senha = 'MinhaS3nh@Segur@'
        
        # Usa o endpoint de setup para criar empresa com senha hashada
        setup_url = reverse('empresa:empresa-setup-senha')
        self.client.post(setup_url, {
            'cnpj': self.cnpj,
            'senha': self.senha
        })

    def test_login_com_credenciais_validas(self):
        """Testa login com CNPJ e senha corretos."""
        url = reverse('empresa:empresa-login')
        data = {
            'cnpj': self.cnpj,
            'senha': self.senha
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica presença dos tokens JWT
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verifica dados da empresa retornados
        self.assertIn('empresa', response.data)
        self.assertIn('uuid', response.data['empresa'])
        self.assertIn('cnpj', response.data['empresa'])
        self.assertIn('nome', response.data['empresa'])
        
        # RN012: Verifica que UUID é retornado (não ID numérico)
        self.assertEqual(response.data['empresa']['cnpj'], self.cnpj)
        self.assertIsInstance(response.data['empresa']['uuid'], str)
        
        # Verifica que não expõe ID numérico
        self.assertNotIn('id', response.data['empresa'])

    def test_login_com_cnpj_invalido(self):
        """Testa login com CNPJ inexistente."""
        url = reverse('empresa:empresa-login')
        data = {
            'cnpj': '99.999.999/0001-99',
            'senha': 'QualquerSenha123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('CNPJ ou senha inválidos', str(response.data))

    def test_login_com_senha_incorreta(self):
        """Testa login com senha errada."""
        url = reverse('empresa:empresa-login')
        data = {
            'cnpj': self.cnpj,
            'senha': 'SenhaErrada123!@#'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('CNPJ ou senha inválidos', str(response.data))

    def test_login_empresa_sem_senha_configurada(self):
        """Testa login de empresa que não tem senha definida."""
        # Cria empresa sem senha
        empresa_sem_senha = MinhaEmpresa.objects.create(cnpj='55.666.777/0001-88')
        
        url = reverse('empresa:empresa-login')
        data = {
            'cnpj': '55.666.777/0001-88',
            'senha': 'QualquerSenha'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Empresa sem senha definida', str(response.data))

    def test_login_sem_cnpj(self):
        """Testa validação de CNPJ obrigatório no login."""
        url = reverse('empresa:empresa-login')
        data = {
            'senha': self.senha
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_sem_senha(self):
        """Testa validação de senha obrigatória no login."""
        url = reverse('empresa:empresa-login')
        data = {
            'cnpj': self.cnpj
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_formato_token_jwt(self):
        """Testa que tokens JWT têm formato correto."""
        url = reverse('empresa:empresa-login')
        data = {
            'cnpj': self.cnpj,
            'senha': self.senha
        }

        response = self.client.post(url, data, format='json')

        # Verifica que tokens são strings não vazias
        self.assertIsInstance(response.data['access'], str)
        self.assertIsInstance(response.data['refresh'], str)
        self.assertGreater(len(response.data['access']), 20)
        self.assertGreater(len(response.data['refresh']), 20)
        
        # Tokens JWT têm 3 partes separadas por ponto
        self.assertEqual(len(response.data['access'].split('.')), 3)
        self.assertEqual(len(response.data['refresh'].split('.')), 3)
