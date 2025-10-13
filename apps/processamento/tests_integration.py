"""
Testes de Integração para o Sistema de Gestão de Notas Fiscais.

Testa o fluxo completo de upload, processamento via Celery e persistência,
usando arquivos reais e verificando o processamento assíncrono.

IMPORTANTE: Estes testes usam o banco de dados de desenvolvimento com transações.
Todas as modificações são revertidas após cada teste para manter integridade dos dados.
"""

import os
import time
from django.test import TestCase, override_settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.db import transaction
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from apps.empresa.models import MinhaEmpresa
from apps.processamento.models import JobProcessamento
from apps.notas.models import NotaFiscal, NotaFiscalItem
from apps.notas.orchestrators import NotaFiscalService
from apps.financeiro.models import LancamentoFinanceiro
from apps.classificadores.models import Classificador


class IntegrationTestBase(TestCase):
    """Base para testes de integração usando transações no banco de desenvolvimento."""

    def setUp(self):
        """Setup inicial para todos os testes de integração."""
        self.client = APIClient()

        # Limpar empresas existentes e criar empresa de teste com CNPJ que corresponde ao arquivo nota-fiscal.jpeg
        MinhaEmpresa.objects.all().delete()  # Limpar todas as empresas existentes

        cnpj_teste = '47.508.411/0008-22'  # CNPJ extraído do arquivo nota-fiscal.jpeg
        cnpj_numero = int(''.join(filter(str.isdigit, cnpj_teste)))
        self.empresa = MinhaEmpresa.objects.create(
            cnpj_numero=cnpj_numero,
            cnpj=cnpj_teste,
            nome='Companhia Brasileira de Distribuição'
        )

        # Garantir classificadores necessários
        Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='PENDENTE',
            defaults={'descricao': 'Aguardando processamento'}
        )
        Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='PROCESSANDO',
            defaults={'descricao': 'Em processamento'}
        )
        Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='CONCLUIDO',
            defaults={'descricao': 'Processamento concluído'}
        )
        Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='FALHA',
            defaults={'descricao': 'Processamento falhou'}
        )

        # URL do endpoint
        self.url = reverse('processar-nota')

import os
import time
from django.test import TransactionTestCase, override_settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.db import transaction
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from apps.empresa.models import MinhaEmpresa
from apps.processamento.models import JobProcessamento
from apps.notas.models import NotaFiscal, NotaFiscalItem
from apps.notas.orchestrators import NotaFiscalService
from apps.financeiro.models import LancamentoFinanceiro
from apps.classificadores.models import Classificador


class IntegrationTestBase(TransactionTestCase):
    """Base para testes de integração usando transações no banco de desenvolvimento."""

    # Configurações para usar banco de desenvolvimento
    databases = {'default'}
    serialized_rollback = True

    @override_settings(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'gestaonotas',
                'USER': 'gestaonotas',
                'PASSWORD': 'gestaonotas_pwd',
                'HOST': 'db',
                'PORT': '5432',
                'TEST': {
                    'NAME': 'gestaonotas',  # Usar o mesmo banco para testes
                }
            }
        }
    )

    def setUp(self):
        """Setup inicial para todos os testes de integração."""
        # Usar APIClient em vez de APITestCase
        self.client = APIClient()

        # Todas as operações devem ser feitas dentro de transações
        with transaction.atomic():
            # Criar empresa de teste (usar get_or_create para evitar conflitos)
            cnpj_teste = '99.999.999/0001-99'
            cnpj_numero = int(''.join(filter(str.isdigit, cnpj_teste)))
            self.empresa, created = MinhaEmpresa.objects.get_or_create(
                cnpj_numero=cnpj_numero,
                defaults={
                    'cnpj': cnpj_teste,
                    'nome': 'Empresa Teste Ltda'
                }
            )

            # Garantir classificadores necessários
            Classificador.objects.get_or_create(
                tipo='STATUS_JOB',
                codigo='PENDENTE',
                defaults={'descricao': 'Aguardando processamento'}
            )
            Classificador.objects.get_or_create(
                tipo='STATUS_JOB',
                codigo='PROCESSANDO',
                defaults={'descricao': 'Em processamento'}
            )
            Classificador.objects.get_or_create(
                tipo='STATUS_JOB',
                codigo='CONCLUIDO',
                defaults={'descricao': 'Processamento concluído'}
            )
            Classificador.objects.get_or_create(
                tipo='STATUS_JOB',
                codigo='FALHA',
                defaults={'descricao': 'Processamento falhou'}
            )

        # URL do endpoint
        self.url = reverse('processar-nota')

    def _upload_arquivo_real(self, caminho_arquivo, nome_arquivo=None):
        """Helper para fazer upload de arquivo real."""
        if not os.path.exists(caminho_arquivo):
            self.skipTest(f"Arquivo de teste não encontrado: {caminho_arquivo}")

        with open(caminho_arquivo, 'rb') as f:
            if nome_arquivo is None:
                nome_arquivo = os.path.basename(caminho_arquivo)

            arquivo = File(f, name=nome_arquivo)
            data = {
                'arquivo': arquivo,
                'meu_cnpj': self.empresa.cnpj
            }

            response = self.client.post(self.url, data, format='multipart')
            return response

    def _aguardar_processamento(self, job_uuid, timeout=60):
        """Aguarda o processamento do job terminar."""
        import time
        from apps.processamento.models import JobProcessamento

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                job = JobProcessamento.objects.get(uuid=job_uuid)
                if job.status.codigo in ['CONCLUIDO', 'FALHA']:
                    return job
            except JobProcessamento.DoesNotExist:
                pass
            time.sleep(1)

        self.fail(f"Job {job_uuid} não terminou processamento em {timeout}s")


class ArquivoRealIntegrationTests(IntegrationTestBase):
    """
    Testes de integração usando arquivos reais do sistema.

    Testa o fluxo completo: upload → processamento via Celery → persistência.
    Usa apenas os arquivos especificados: nota-fiscal.jpeg e test_nota.pdf
    """

    def test_upload_e_processamento_nota_fiscal_jpeg(self):
        """
        Testa upload e processamento completo usando nota-fiscal.jpeg real.

        Este teste verifica:
        - Upload bem-sucedido retorna 202
        - Job é criado com UUID
        - Celery processa o job
        - Dados são extraídos via LLM
        - Nota fiscal e lançamento são persistidos
        """
        caminho_arquivo = 'media/notas_fiscais_uploads/nota-fiscal.jpeg'

        # Upload do arquivo
        response = self._upload_arquivo_real(caminho_arquivo)

        # Verificar resposta do upload
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('uuid', response.data)
        job_uuid = response.data['uuid']

        # Aguardar processamento terminar
        job = self._aguardar_processamento(job_uuid)

        # Verificar que processamento foi bem-sucedido
        self.assertEqual(job.status.codigo, 'CONCLUIDO')

        # Verificar que nota fiscal foi criada
        self.assertTrue(NotaFiscal.objects.filter(job_origem=job).exists())
        nota_fiscal = NotaFiscal.objects.filter(job_origem=job).first()

        # Verificar que lançamento financeiro foi criado
        self.assertTrue(LancamentoFinanceiro.objects.filter(nota_fiscal=nota_fiscal).exists())
        lancamento = LancamentoFinanceiro.objects.filter(nota_fiscal=nota_fiscal).first()

        # Verificar dados básicos foram extraídos
        self.assertIsNotNone(nota_fiscal.numero)
        self.assertIsNotNone(nota_fiscal.valor_total)
        self.assertGreater(nota_fiscal.valor_total, 0)

    def test_upload_e_processamento_test_nota_pdf(self):
        """
        Testa upload e processamento usando test_nota.pdf.

        Nota: Este arquivo é um PDF corrompido (apenas texto "Test PDF content"),
        então deve falhar na extração, mas o fluxo deve ser testado.
        """
        caminho_arquivo = 'media/notas_fiscais_uploads/test_nota.pdf'

        # Upload do arquivo
        response = self._upload_arquivo_real(caminho_arquivo)

        # Verificar resposta do upload
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('uuid', response.data)
        job_uuid = response.data['uuid']

        # Aguardar processamento terminar
        job = self._aguardar_processamento(job_uuid)

        # Como o PDF está corrompido, deve falhar
        self.assertEqual(job.status.codigo, 'FALHA')

        # Verificar que não criou nota fiscal (processamento falhou)
        self.assertFalse(NotaFiscal.objects.filter(job_origem=job).exists())


class LLMIntegrationTests(IntegrationTestBase):
    """
    Testes de integração com LLM - versão econômica.

    Usa mocks para minimizar custos da API do Gemini.
    """

    @patch('apps.notas.llm.orchestrator.DocumentProcessor.process_file')
    def test_llm_extracao_mockada_sucesso(self, mock_process_file):
        """
        Testa extração LLM com mock - simula sucesso.

        Minimiza custos: não chama API real do Gemini.
        """
        # Mock da resposta do LLM
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.tipo_documento = 'nf_produto'
        mock_result.dados_extraidos = MagicMock()
        mock_result.dados_extraidos.numero = '12345'
        mock_result.dados_extraidos.data_emissao = '2025-01-15'
        mock_result.dados_extraidos.data_vencimento = '2025-02-15'
        mock_result.dados_extraidos.valor_total = 1500.00
        mock_result.dados_extraidos.emissor = MagicMock()
        mock_result.dados_extraidos.emissor.cnpj_cpf = '11.111.111/0001-11'
        mock_result.dados_extraidos.emissor.nome = 'Fornecedor Mock'
        mock_result.dados_extraidos.destinatario = MagicMock()
        mock_result.dados_extraidos.destinatario.cnpj_cpf = '99.999.999/0001-99'
        mock_result.dados_extraidos.destinatario.nome = 'Empresa Teste'

        mock_process_file.return_value = mock_result

        # Criar arquivo fake para upload
        arquivo = SimpleUploadedFile(
            'nota_mock.pdf',
            b'conteudo mockado',
            content_type='application/pdf'
        )

        data = {
            'arquivo': arquivo,
            'meu_cnpj': self.empresa.cnpj
        }

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        job_uuid = response.data['uuid']
        job = self._aguardar_processamento(job_uuid)

        # Verificar sucesso
        self.assertEqual(job.status.codigo, 'CONCLUIDO')

        # Verificar que LLM foi chamado
        mock_process_file.assert_called_once()

        # Verificar persistência
        self.assertTrue(NotaFiscal.objects.filter(job_origem=job).exists())

    @patch('apps.notas.llm.orchestrator.DocumentProcessor.process_file')
    def test_llm_extracao_mockada_falha_sem_fallback(self, mock_process_file):
        """
        Testa que quando LLM falha, não há fallback automático.

        Verifica que o sistema respeita a independência dos métodos de extração.
        """
        # Mock de falha do LLM
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Documento ilegível"
        mock_process_file.return_value = mock_result

        # Criar arquivo fake
        arquivo = SimpleUploadedFile(
            'nota_ilegivel.pdf',
            b'documento ilegivel',
            content_type='application/pdf'
        )

        data = {
            'arquivo': arquivo,
            'meu_cnpj': self.empresa.cnpj
        }

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        job_uuid = response.data['uuid']
        job = self._aguardar_processamento(job_uuid)

        # Deve falhar (sem fallback)
        self.assertEqual(job.status.codigo, 'FALHA')

        # Verificar que LLM foi chamado
        mock_process_file.assert_called_once()

        # Verificar que não criou nota fiscal
        self.assertFalse(NotaFiscal.objects.filter(job_origem=job).exists())


class CeleryQueueIntegrationTests(IntegrationTestBase):
    """
    Testes de integração para verificar processamento de filas Celery.

    Testa que jobs são enfileirados e processados corretamente.
    """

    def test_multiplos_jobs_processamento_sequencial(self):
        """
        Testa que múltiplos jobs são processados sequencialmente pela fila.
        Usa apenas os arquivos especificados: nota-fiscal.jpeg (sucesso) e test_nota.pdf (falha)
        """
        # Usar os dois arquivos especificados
        arquivos_teste = [
            ('media/notas_fiscais_uploads/nota-fiscal.jpeg', 'nota-fiscal.jpeg'),
            ('media/notas_fiscais_uploads/test_nota.pdf', 'test_nota.pdf')
        ]

        # Fazer upload dos arquivos
        job_uuids = []
        for caminho_arquivo, nome_arquivo in arquivos_teste:
            response = self._upload_arquivo_real(caminho_arquivo, nome_arquivo)
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            job_uuids.append(response.data['uuid'])

        # Aguardar todos terminarem
        jobs = []
        for job_uuid in job_uuids:
            job = self._aguardar_processamento(job_uuid)
            jobs.append(job)

        # Verificar resultados esperados
        # Primeiro job (nota-fiscal.jpeg) deve ser bem-sucedido
        self.assertEqual(jobs[0].status.codigo, 'CONCLUIDO')
        self.assertTrue(NotaFiscal.objects.filter(job_origem=jobs[0]).exists())

        # Segundo job (test_nota.pdf) deve falhar
        self.assertEqual(jobs[1].status.codigo, 'FALHA')
        self.assertFalse(NotaFiscal.objects.filter(job_origem=jobs[1]).exists())

        # Verificar que todos foram processados (timestamps de conclusão)
        for job in jobs:
            self.assertIsNotNone(job.dt_conclusao)

    @patch('apps.notas.llm.orchestrator.DocumentProcessor.process_file')
    def test_job_reprocessamento_apos_falha(self, mock_process_file):
        """
        Testa reprocessamento de job após falha temporária.
        """
        # Primeiro mock: falha
        mock_result_fail = MagicMock()
        mock_result_fail.success = False
        mock_result_fail.error = "Erro temporário"

        # Segundo mock: sucesso
        mock_result_success = MagicMock()
        mock_result_success.success = True
        mock_result_success.tipo_documento = 'nf_produto'
        mock_result_success.dados_extraidos = MagicMock()
        mock_result_success.dados_extraidos.numero = '99999'
        mock_result_success.dados_extraidos.data_emissao = '2025-01-20'
        mock_result_success.dados_extraidos.data_vencimento = '2025-02-20'
        mock_result_success.dados_extraidos.valor_total = 2500.00
        mock_result_success.dados_extraidos.emissor = MagicMock()
        mock_result_success.dados_extraidos.emissor.cnpj_cpf = '22.222.222/0001-22'
        mock_result_success.dados_extraidos.emissor.nome = 'Fornecedor Reprocessado'
        mock_result_success.dados_extraidos.destinatario = MagicMock()
        mock_result_success.dados_extraidos.destinatario.cnpj_cpf = '99.999.999/0001-99'
        mock_result_success.dados_extraidos.destinatario.nome = 'Empresa Teste'

        # Primeiro processamento falha
        mock_process_file.return_value = mock_result_fail

        arquivo = SimpleUploadedFile(
            'nota_retry.pdf',
            b'teste retry',
            content_type='application/pdf'
        )

        data = {
            'arquivo': arquivo,
            'meu_cnpj': self.empresa.cnpj
        }

        response = self.client.post(self.url, data, format='multipart')
        job_uuid = response.data['uuid']
        job = self._aguardar_processamento(job_uuid)

        # Primeiro processamento deve falhar
        self.assertEqual(job.status.codigo, 'FALHA')
        self.assertFalse(NotaFiscal.objects.filter(job_origem=job).exists())

        # Simular reprocessamento (mudar mock para sucesso)
        mock_process_file.return_value = mock_result_success

        # Reprocessar o mesmo job (simulando retry manual)
        service = NotaFiscalService()
        lancamento = service.processar_nota_fiscal_do_job(job)

        # Verificar que agora foi bem-sucedido
        job.refresh_from_db()
        self.assertEqual(job.status.codigo, 'CONCLUIDO')
        self.assertTrue(NotaFiscal.objects.filter(job_origem=job).exists())

    def test_fila_celery_worker_ativo(self):
        """
        Testa que o worker Celery está ativo e processando tarefas.
        Usa o arquivo nota-fiscal.jpeg para teste.
        """
        from apps.processamento.tasks import processar_nota_fiscal_task

        # Verificar que a task está registrada
        self.assertTrue(hasattr(processar_nota_fiscal_task, 'delay'))

        # Fazer upload usando arquivo real
        caminho_arquivo = 'media/notas_fiscais_uploads/nota-fiscal.jpeg'
        response = self._upload_arquivo_real(caminho_arquivo)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        job_uuid = response.data['uuid']
        job = self._aguardar_processamento(job_uuid)

        # Verificar que o job foi processado com sucesso
        self.assertEqual(job.status.codigo, 'CONCLUIDO')

        # Verificar que nota fiscal foi criada
        self.assertTrue(NotaFiscal.objects.filter(job_origem=job).exists())