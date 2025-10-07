"""
Testes para o app dashboard.
Testa endpoint de estatísticas consolidadas.
"""
from decimal import Decimal
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.empresa.models import MinhaEmpresa
from apps.parceiros.models import Parceiro
from apps.notas.models import NotaFiscal
from apps.financeiro.models import LancamentoFinanceiro
from apps.processamento.models import JobProcessamento
from apps.classificadores.models import Classificador


class DashboardStatsTestCase(APITestCase):
    """
    REMOVIDO: Testes GET não são necessários.
    Dashboard apenas consulta dados, não modifica.
    """
    pass

    def setUp(self):
        """Prepara dados iniciais para os testes."""
        # Cria empresa
        self.empresa = MinhaEmpresa.objects.create(
            cnpj='12.345.678/0001-99',
            nome='Minha Empresa'
        )
        
        # Cria classificadores
        self.clf_tipo_pagar = Classificador.objects.get_or_create(
            tipo='TIPO_LANCAMENTO',
            codigo='PAGAR',
            defaults={'descricao': 'Conta a Pagar'}
        )[0]
        
        self.clf_status_pendente = Classificador.objects.get_or_create(
            tipo='STATUS_LANCAMENTO',
            codigo='PENDENTE',
            defaults={'descricao': 'Pendente'}
        )[0]
        
        self.clf_tipo_fornecedor = Classificador.objects.get_or_create(
            tipo='TIPO_PARCEIRO',
            codigo='FORNECEDOR',
            defaults={'descricao': 'Fornecedor'}
        )[0]
        
        self.clf_status_job = Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='CONCLUIDO',
            defaults={'descricao': 'Concluído'}
        )[0]
        
        # Cria job
        self.job = JobProcessamento.objects.create(
            empresa=self.empresa,
            status=self.clf_status_job
        )

    def test_top_5_fornecedores_pendentes(self):
        """
        RF008: Testa que dashboard retorna top 5 fornecedores.
        Deve consolidar valores por fornecedor e ordenar por total.
        """
        # Cria 6 fornecedores com valores diferentes
        fornecedores = []
        valores = [Decimal('10000.00'), Decimal('8000.00'), Decimal('6000.00'),
                  Decimal('4000.00'), Decimal('2000.00'), Decimal('1000.00')]
        
        for i, valor in enumerate(valores):
            fornecedor = Parceiro.objects.create(
                nome=f'Fornecedor {i+1}',
                cnpj=f'{str(i+1).zfill(2)}.{str(i+1).zfill(3)}.{str(i+1).zfill(3)}/0001-{str(i+1).zfill(2)}',
                clf_tipo=self.clf_tipo_fornecedor
            )
            
            nota = NotaFiscal.objects.create(
                job_origem=self.job,
                parceiro=fornecedor,
                numero=f'NF-{i+1}',
                data_emissao=date.today(),
                valor_total=valor
            )
            
            LancamentoFinanceiro.objects.create(
                nota_fiscal=nota,
                descricao=f'Compra fornecedor {i+1}',
                valor=valor,
                clf_tipo=self.clf_tipo_pagar,
                clf_status=self.clf_status_pendente,
                data_vencimento=date.today() + timedelta(days=30)
            )
        
        url = reverse('dashboard-stats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('top_5_fornecedores_pendentes', response.data)
        
        # Deve retornar apenas 5 fornecedores (não 6)
        self.assertEqual(len(response.data['top_5_fornecedores_pendentes']), 5)
        
        # Deve estar ordenado por valor (maior primeiro)
        top_5 = response.data['top_5_fornecedores_pendentes']
        self.assertEqual(top_5[0]['nome'], 'Fornecedor 1')
        self.assertEqual(str(top_5[0]['total_a_pagar']), '10000.00')
        self.assertEqual(top_5[4]['nome'], 'Fornecedor 5')
        self.assertEqual(str(top_5[4]['total_a_pagar']), '2000.00')
        
        # O fornecedor 6 (menor valor) não deve aparecer
        nomes = [f['nome'] for f in top_5]
        self.assertNotIn('Fornecedor 6', nomes)

    def test_consolidar_multiplas_notas_mesmo_fornecedor(self):
        """
        Testa que valores de múltiplas notas do mesmo fornecedor são consolidados.
        """
        fornecedor = Parceiro.objects.create(
            nome='Fornecedor Consolidado',
            cnpj='55.555.555/0001-55',
            clf_tipo=self.clf_tipo_fornecedor
        )
        
        # Cria 3 notas para o mesmo fornecedor
        valores = [Decimal('1000.00'), Decimal('2000.00'), Decimal('3000.00')]
        
        for i, valor in enumerate(valores):
            nota = NotaFiscal.objects.create(
                job_origem=self.job,
                parceiro=fornecedor,
                numero=f'NF-CONS-{i+1}',
                data_emissao=date.today(),
                valor_total=valor
            )
            
            LancamentoFinanceiro.objects.create(
                nota_fiscal=nota,
                descricao=f'Compra {i+1}',
                valor=valor,
                clf_tipo=self.clf_tipo_pagar,
                clf_status=self.clf_status_pendente,
                data_vencimento=date.today() + timedelta(days=30)
            )
        
        url = reverse('dashboard-stats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve ter apenas 1 fornecedor consolidado
        top_5 = response.data['top_5_fornecedores_pendentes']
        self.assertEqual(len(top_5), 1)
        
        # Total deve ser soma de todas as notas
        self.assertEqual(top_5[0]['nome'], 'Fornecedor Consolidado')
        self.assertEqual(str(top_5[0]['total_a_pagar']), '6000.00')

    def test_dashboard_vazio_sem_lancamentos(self):
        """Testa que dashboard retorna lista vazia quando não há lançamentos."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['top_5_fornecedores_pendentes']), 0)

    def test_dashboard_retorna_cnpj_fornecedor(self):
        """Testa que dashboard retorna CNPJ dos fornecedores."""
        fornecedor = Parceiro.objects.create(
            nome='Fornecedor Teste CNPJ',
            cnpj='77.888.999/0001-77',
            clf_tipo=self.clf_tipo_fornecedor
        )
        
        nota = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=fornecedor,
            numero='NF-CNPJ',
            data_emissao=date.today(),
            valor_total=Decimal('5000.00')
        )
        
        LancamentoFinanceiro.objects.create(
            nota_fiscal=nota,
            descricao='Compra teste CNPJ',
            valor=Decimal('5000.00'),
            clf_tipo=self.clf_tipo_pagar,
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=30)
        )
        
        url = reverse('dashboard-stats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        top_5 = response.data['top_5_fornecedores_pendentes']
        self.assertEqual(len(top_5), 1)
        
        # Deve retornar nome e CNPJ
        self.assertEqual(top_5[0]['nome'], 'Fornecedor Teste CNPJ')
        self.assertEqual(top_5[0]['cnpj'], '77.888.999/0001-77')
