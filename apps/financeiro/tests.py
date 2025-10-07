"""
Testes para o app financeiro.
Testa listagem de contas a pagar e contas a receber.
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


class ContasAPagarTestCase(APITestCase):
    """
    REMOVIDO: Testes GET não são necessários.
    Contas a pagar são criadas automaticamente pelo processamento de notas.
    Não há endpoint POST/PATCH para criar/editar manualmente.
    """
    pass

    def setUp(self):
        """Prepara dados iniciais para os testes."""
        # Cria empresa
        self.empresa = MinhaEmpresa.objects.create(
            cnpj='12.345.678/0001-99',
            nome='Minha Empresa'
        )
        
        # Cria classificadores necessários
        self.clf_tipo_pagar = Classificador.objects.get_or_create(
            tipo='TIPO_LANCAMENTO',
            codigo='PAGAR',
            defaults={'descricao': 'Conta a Pagar'}
        )[0]
        
        self.clf_tipo_receber = Classificador.objects.get_or_create(
            tipo='TIPO_LANCAMENTO',
            codigo='RECEBER',
            defaults={'descricao': 'Conta a Receber'}
        )[0]
        
        self.clf_status_pendente = Classificador.objects.get_or_create(
            tipo='STATUS_LANCAMENTO',
            codigo='PENDENTE',
            defaults={'descricao': 'Pendente'}
        )[0]
        
        self.clf_status_pago = Classificador.objects.get_or_create(
            tipo='STATUS_LANCAMENTO',
            codigo='PAGO',
            defaults={'descricao': 'Pago'}
        )[0]
        
        self.clf_tipo_fornecedor = Classificador.objects.get_or_create(
            tipo='TIPO_PARCEIRO',
            codigo='FORNECEDOR',
            defaults={'descricao': 'Fornecedor'}
        )[0]
        
        self.clf_tipo_cliente = Classificador.objects.get_or_create(
            tipo='TIPO_PARCEIRO',
            codigo='CLIENTE',
            defaults={'descricao': 'Cliente'}
        )[0]
        
        self.clf_status_job = Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='CONCLUIDO',
            defaults={'descricao': 'Concluído'}
        )[0]
        
        # Cria fornecedores
        self.fornecedor1 = Parceiro.objects.create(
            nome='Fornecedor ABC',
            cnpj='11.111.111/0001-11',
            clf_tipo=self.clf_tipo_fornecedor
        )
        
        self.fornecedor2 = Parceiro.objects.create(
            nome='Fornecedor XYZ',
            cnpj='22.222.222/0001-22',
            clf_tipo=self.clf_tipo_fornecedor
        )
        
        # Cria job de processamento
        self.job = JobProcessamento.objects.create(
            empresa=self.empresa,
            status=self.clf_status_job
        )

    def test_listar_contas_a_pagar_pendentes(self):
        """
        RF006 e RN014: Lista apenas lançamentos tipo PAGAR e status PENDENTE.
        Deve ordenar por data de vencimento.
        """
        # Cria notas fiscais
        nota1 = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.fornecedor1,
            numero='NF-001',
            data_emissao=date.today(),
            valor_total=Decimal('1500.00')
        )
        
        nota2 = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.fornecedor2,
            numero='NF-002',
            data_emissao=date.today(),
            valor_total=Decimal('2500.00')
        )
        
        # Cria lançamentos a pagar (empresa é destinatário)
        # Vencimento mais próximo
        lanc1 = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota1,
            descricao='Compra de materiais',
            valor=Decimal('1500.00'),
            clf_tipo=self.clf_tipo_pagar,
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=10)
        )
        
        # Vencimento mais distante
        lanc2 = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota2,
            descricao='Compra de equipamentos',
            valor=Decimal('2500.00'),
            clf_tipo=self.clf_tipo_pagar,
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=30)
        )
        
        url = reverse('contas-a-pagar')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # RN014: Deve ordenar por data de vencimento (mais próximo primeiro)
        self.assertEqual(response.data[0]['descricao'], 'Compra de materiais')
        self.assertEqual(response.data[1]['descricao'], 'Compra de equipamentos')
        
        # RN012: Deve retornar UUID, não ID numérico
        self.assertIn('uuid', response.data[0])
        self.assertNotIn('id', response.data[0])

    def test_nao_listar_contas_pagas(self):
        """
        RN014: Não deve listar lançamentos com status PAGO.
        Apenas PENDENTE deve aparecer.
        """
        nota = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.fornecedor1,
            numero='NF-003',
            data_emissao=date.today(),
            valor_total=Decimal('1000.00')
        )
        
        # Lançamento PENDENTE
        lanc_pendente = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota,
            descricao='Compra pendente',
            valor=Decimal('500.00'),
            clf_tipo=self.clf_tipo_pagar,
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=15)
        )
        
        # Cria outra nota para lançamento pago
        nota2 = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.fornecedor2,
            numero='NF-004',
            data_emissao=date.today(),
            valor_total=Decimal('500.00')
        )
        
        # Lançamento já PAGO (não deve aparecer)
        lanc_pago = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota2,
            descricao='Compra já paga',
            valor=Decimal('500.00'),
            clf_tipo=self.clf_tipo_pagar,
            clf_status=self.clf_status_pago,
            data_vencimento=date.today() - timedelta(days=5),
            data_pagamento=date.today() - timedelta(days=2)
        )
        
        url = reverse('contas-a-pagar')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve listar apenas o lançamento pendente
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['descricao'], 'Compra pendente')

    def test_nao_listar_contas_a_receber(self):
        """
        RN014: Não deve listar lançamentos tipo RECEBER.
        Endpoint de contas a pagar deve filtrar apenas PAGAR.
        """
        nota = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.fornecedor1,
            numero='NF-005',
            data_emissao=date.today(),
            valor_total=Decimal('3000.00')
        )
        
        # Lançamento tipo RECEBER (não deve aparecer em contas a pagar)
        lanc_receber = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota,
            descricao='Venda de produtos',
            valor=Decimal('3000.00'),
            clf_tipo=self.clf_tipo_receber,  # RECEBER, não PAGAR
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=20)
        )
        
        url = reverse('contas-a-pagar')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Não deve listar nada, pois é tipo RECEBER
        self.assertEqual(len(response.data), 0)

    def test_lista_vazia_sem_lancamentos(self):
        """Testa que retorna lista vazia quando não há lançamentos."""
        url = reverse('contas-a-pagar')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class ContasAReceberTestCase(APITestCase):
    """
    REMOVIDO: Testes GET não são necessários.
    Contas a receber são criadas automaticamente pelo processamento de notas.
    Não há endpoint POST/PATCH para criar/editar manualmente.
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
        self.clf_tipo_receber = Classificador.objects.get_or_create(
            tipo='TIPO_LANCAMENTO',
            codigo='RECEBER',
            defaults={'descricao': 'Conta a Receber'}
        )[0]
        
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
        
        self.clf_status_recebido = Classificador.objects.get_or_create(
            tipo='STATUS_LANCAMENTO',
            codigo='RECEBIDO',
            defaults={'descricao': 'Recebido'}
        )[0]
        
        self.clf_tipo_cliente = Classificador.objects.get_or_create(
            tipo='TIPO_PARCEIRO',
            codigo='CLIENTE',
            defaults={'descricao': 'Cliente'}
        )[0]
        
        self.clf_status_job = Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='CONCLUIDO',
            defaults={'descricao': 'Concluído'}
        )[0]
        
        # Cria clientes
        self.cliente1 = Parceiro.objects.create(
            nome='Cliente Alpha',
            cnpj='33.333.333/0001-33',
            clf_tipo=self.clf_tipo_cliente
        )
        
        self.cliente2 = Parceiro.objects.create(
            nome='Cliente Beta',
            cnpj='44.444.444/0001-44',
            clf_tipo=self.clf_tipo_cliente
        )
        
        # Cria job
        self.job = JobProcessamento.objects.create(
            empresa=self.empresa,
            status=self.clf_status_job
        )

    def test_listar_contas_a_receber_pendentes(self):
        """
        RF007 e RN014: Lista apenas lançamentos tipo RECEBER e status PENDENTE.
        Deve ordenar por data de vencimento.
        """
        # Cria notas fiscais
        nota1 = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.cliente1,
            numero='NF-101',
            data_emissao=date.today(),
            valor_total=Decimal('5000.00')
        )
        
        nota2 = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.cliente2,
            numero='NF-102',
            data_emissao=date.today(),
            valor_total=Decimal('7500.00')
        )
        
        # Lançamentos a receber (empresa é remetente)
        lanc1 = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota1,
            descricao='Venda de produtos linha A',
            valor=Decimal('5000.00'),
            clf_tipo=self.clf_tipo_receber,
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=15)
        )
        
        lanc2 = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota2,
            descricao='Venda de produtos linha B',
            valor=Decimal('7500.00'),
            clf_tipo=self.clf_tipo_receber,
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=45)
        )
        
        url = reverse('contas-a-receber')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Deve ordenar por vencimento (mais próximo primeiro)
        self.assertEqual(response.data[0]['descricao'], 'Venda de produtos linha A')
        self.assertEqual(response.data[1]['descricao'], 'Venda de produtos linha B')
        
        # Deve retornar UUID
        self.assertIn('uuid', response.data[0])
        self.assertNotIn('id', response.data[0])

    def test_nao_listar_contas_recebidas(self):
        """Não deve listar lançamentos com status RECEBIDO."""
        nota = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.cliente1,
            numero='NF-103',
            data_emissao=date.today(),
            valor_total=Decimal('2000.00')
        )
        
        # Lançamento já recebido
        lanc_recebido = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota,
            descricao='Venda já recebida',
            valor=Decimal('2000.00'),
            clf_tipo=self.clf_tipo_receber,
            clf_status=self.clf_status_recebido,
            data_vencimento=date.today() - timedelta(days=10),
            data_pagamento=date.today() - timedelta(days=5)
        )
        
        url = reverse('contas-a-receber')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_nao_listar_contas_a_pagar(self):
        """Não deve listar lançamentos tipo PAGAR no endpoint de receber."""
        nota = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.cliente1,
            numero='NF-104',
            data_emissao=date.today(),
            valor_total=Decimal('1000.00')
        )
        
        # Lançamento tipo PAGAR
        lanc_pagar = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota,
            descricao='Compra de insumos',
            valor=Decimal('1000.00'),
            clf_tipo=self.clf_tipo_pagar,  # PAGAR, não RECEBER
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=20)
        )
        
        url = reverse('contas-a-receber')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_valores_corretos(self):
        """
        RN009: Verifica que valores são retornados corretamente.
        Precisão decimal deve ser mantida.
        """
        nota = NotaFiscal.objects.create(
            job_origem=self.job,
            parceiro=self.cliente1,
            numero='NF-105',
            data_emissao=date.today(),
            valor_total=Decimal('1234.56')
        )
        
        lanc = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota,
            descricao='Venda com valor específico',
            valor=Decimal('1234.56'),
            clf_tipo=self.clf_tipo_receber,
            clf_status=self.clf_status_pendente,
            data_vencimento=date.today() + timedelta(days=30)
        )
        
        url = reverse('contas-a-receber')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica precisão decimal (2 casas)
        self.assertEqual(str(response.data[0]['valor']), '1234.56')
