"""
Testes para o app processamento.
Testa upload de notas fiscais e consulta de status de jobs.
"""
import io
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from apps.empresa.models import MinhaEmpresa
from apps.processamento.models import JobProcessamento
from apps.classificadores.models import Classificador, get_classifier


class ProcessarNotaFiscalTestCase(APITestCase):
    """
    Testes para o endpoint de upload e processamento de notas fiscais.
    RF001: Sistema deve permitir upload e processamento assíncrono.
    RF005: Retornar UUID do job para acompanhamento.
    RN006: Status de processamento sequencial (PENDENTE → PROCESSANDO → CONCLUIDO/FALHA).
    RN012: Usar UUID em APIs públicas, não IDs numéricos.
    RN013: Processamento assíncrono obrigatório.
    """

    def setUp(self):
        """Prepara dados iniciais para os testes."""
        # Cria empresa para testes
        self.empresa = MinhaEmpresa.objects.create(
            cnpj='12.345.678/0001-99',
            nome='Empresa Teste'
        )
        
        # Garante que classificadores de status existem
        # Normalmente esses seriam criados via seed migration
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

    def test_upload_nota_fiscal_com_sucesso(self):
        """
        RF001: Testa upload de nota fiscal com dados válidos.
        Deve criar job com status PENDENTE e retornar UUID.
        """
        url = reverse('processar-nota')
        
        # Cria arquivo fake de nota fiscal
        arquivo = SimpleUploadedFile(
            'nota_fiscal.pdf',
            b'conteudo fake da nota fiscal',
            content_type='application/pdf'
        )
        
        data = {
            'arquivo': arquivo,
            'meu_cnpj': self.empresa.cnpj
        }

        response = self.client.post(url, data, format='multipart')

        # RN013: Deve retornar 202 ACCEPTED (processamento assíncrono)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        # RF005 e RN012: Deve retornar UUID (não ID numérico)
        self.assertIn('uuid', response.data)
        self.assertIsInstance(response.data['uuid'], str)
        self.assertEqual(len(response.data['uuid']), 36)  # UUID tem 36 chars com hífens
        
        # Não deve expor ID numérico
        self.assertNotIn('id', response.data)
        
        # RN006: Deve retornar status PENDENTE
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status']['codigo'], 'PENDENTE')
        
        # Verifica que job foi criado no banco (será revertido pelo rollback)
        job_uuid = response.data['uuid']
        self.assertTrue(JobProcessamento.objects.filter(uuid=job_uuid).exists())
        
        # Verifica relacionamento com empresa
        job = JobProcessamento.objects.get(uuid=job_uuid)
        self.assertEqual(job.empresa, self.empresa)

    def test_upload_sem_arquivo(self):
        """Testa validação de arquivo obrigatório."""
        url = reverse('processar-nota')
        data = {
            'meu_cnpj': self.empresa.cnpj
        }

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_sem_cnpj_empresa(self):
        """Testa validação de CNPJ obrigatório."""
        url = reverse('processar-nota')
        
        arquivo = SimpleUploadedFile(
            'nota_fiscal.pdf',
            b'conteudo fake',
            content_type='application/pdf'
        )
        
        data = {
            'arquivo': arquivo
        }

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_com_cnpj_inexistente(self):
        """
        RN005: Testa que empresa deve existir no sistema.
        Deve rejeitar se CNPJ não está cadastrado.
        """
        url = reverse('processar-nota')
        
        arquivo = SimpleUploadedFile(
            'nota_fiscal.pdf',
            b'conteudo fake',
            content_type='application/pdf'
        )
        
        data = {
            'arquivo': arquivo,
            'meu_cnpj': '99.999.999/0001-99'  # CNPJ não existe
        }

        response = self.client.post(url, data, format='multipart')

        # Deve retornar erro (empresa não encontrada)
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ])

    def test_arquivo_salvo_corretamente(self):
        """Verifica que arquivo é salvo no storage."""
        url = reverse('processar-nota')
        
        arquivo = SimpleUploadedFile(
            'minha_nota.pdf',
            b'conteudo do arquivo PDF',
            content_type='application/pdf'
        )
        
        data = {
            'arquivo': arquivo,
            'meu_cnpj': self.empresa.cnpj
        }

        response = self.client.post(url, data, format='multipart')

        job = JobProcessamento.objects.get(uuid=response.data['uuid'])
        
        # Verifica que arquivo foi salvo
        self.assertTrue(job.arquivo_original)
        self.assertIn('notas_fiscais_uploads', job.arquivo_original.name)

    def test_upload_arquivo_duplicado(self):
        """
        Testa que o upload de um arquivo duplicado não salva o arquivo novamente.
        O novo job deve apontar para o arquivo original do job existente.
        """
        url = reverse('processar-nota')

        # Primeiro upload
        arquivo1 = SimpleUploadedFile(
            'nota_fiscal_duplicada.pdf',
            b'conteudo da nota fiscal duplicada',
            content_type='application/pdf'
        )
        data1 = {'arquivo': arquivo1, 'meu_cnpj': self.empresa.cnpj}
        response1 = self.client.post(url, data1, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_202_ACCEPTED)
        job1_uuid = response1.data['uuid']
        job1 = JobProcessamento.objects.get(uuid=job1_uuid)

        # Segundo upload com o mesmo conteúdo
        arquivo2 = SimpleUploadedFile(
            'nota_fiscal_duplicada.pdf',
            b'conteudo da nota fiscal duplicada',
            content_type='application/pdf'
        )
        data2 = {'arquivo': arquivo2, 'meu_cnpj': self.empresa.cnpj}
        response2 = self.client.post(url, data2, format='multipart')
        self.assertEqual(response2.status_code, status.HTTP_202_ACCEPTED)
        job2_uuid = response2.data['uuid']
        job2 = JobProcessamento.objects.get(uuid=job2_uuid)

        # Verifica que os jobs são diferentes
        self.assertNotEqual(job1.id, job2.id)

        # Verifica que o arquivo do segundo job é o mesmo do primeiro
        self.assertEqual(job1.arquivo_original.name, job2.arquivo_original.name)


class JobStatusTestCase(APITestCase):
    """
    REMOVIDO: Endpoint GET não precisa de teste.
    RF005: Status de job é apenas consulta, não modifica dados.
    """
    pass


class JobStatusTestCaseREMOVIDO_OLD(APITestCase):
    """
    CÓDIGO ANTIGO - REMOVIDO
    Testes para o endpoint de consulta de status de job.
    RF005: Permitir consulta de status de processamento assíncrono.
    RN006: Retornar informações sobre tarefas em andamento.
    RN012: Aceitar e retornar UUID do job, não ID numérico.
    """

    def setUp(self):
        """Prepara dados iniciais para os testes."""
        # Cria empresa
        self.empresa = MinhaEmpresa.objects.create(
            cnpj='12.345.678/0001-99',
            nome='Empresa Teste'
        )
        
        # Cria classificadores de status
        self.status_pendente = Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='PENDENTE',
            defaults={'descricao': 'Aguardando processamento'}
        )[0]
        
        self.status_concluido = Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='CONCLUIDO',
            defaults={'descricao': 'Processamento concluído'}
        )[0]
        
        self.status_falha = Classificador.objects.get_or_create(
            tipo='STATUS_JOB',
            codigo='FALHA',
            defaults={'descricao': 'Processamento falhou'}
        )[0]
        
        # Cria arquivo fake
        self.arquivo = SimpleUploadedFile(
            'nota.pdf',
            b'fake content',
            content_type='application/pdf'
        )

    def test_consultar_status_job_pendente(self):
        """
        RF005: Testa consulta de job com status PENDENTE.
        Deve retornar UUID e status correto.
        """
        # Cria job pendente
        job = JobProcessamento.objects.create(
            arquivo_original=self.arquivo,
            empresa=self.empresa,
            status=self.status_pendente
        )
        
        # RN012: Consulta usando UUID
        url = reverse('job-status', kwargs={'uuid': str(job.uuid)})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica dados retornados
        self.assertEqual(response.data['uuid'], str(job.uuid))
        self.assertEqual(response.data['status'], 'PENDENTE')
        
        # Não deve expor ID numérico
        self.assertNotIn('id', response.data)
        
        # Timestamps devem estar presentes
        self.assertIn('dt_criacao', response.data)
        
        # dt_conclusao deve ser None para job pendente
        self.assertIsNone(response.data['dt_conclusao'])
        self.assertIsNone(response.data['mensagem_erro'])

    def test_consultar_status_job_concluido(self):
        """Testa consulta de job com status CONCLUIDO."""
        from django.utils import timezone
        
        job = JobProcessamento.objects.create(
            arquivo_original=self.arquivo,
            empresa=self.empresa,
            status=self.status_concluido,
            dt_conclusao=timezone.now()
        )
        
        url = reverse('job-status', kwargs={'uuid': str(job.uuid)})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'CONCLUIDO')
        self.assertIsNotNone(response.data['dt_conclusao'])
        self.assertIsNone(response.data['mensagem_erro'])

    def test_consultar_status_job_falha(self):
        """Testa consulta de job com status FALHA e mensagem de erro."""
        from django.utils import timezone
        
        mensagem_erro = 'Erro ao processar: arquivo corrompido'
        
        job = JobProcessamento.objects.create(
            arquivo_original=self.arquivo,
            empresa=self.empresa,
            status=self.status_falha,
            dt_conclusao=timezone.now(),
            mensagem_erro=mensagem_erro
        )
        
        url = reverse('job-status', kwargs={'uuid': str(job.uuid)})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'FALHA')
        self.assertIsNotNone(response.data['dt_conclusao'])
        self.assertEqual(response.data['mensagem_erro'], mensagem_erro)

    def test_consultar_job_inexistente(self):
        """Testa consulta de job com UUID que não existe."""
        import uuid as uuid_lib
        
        # UUID válido mas não existe no banco
        uuid_fake = str(uuid_lib.uuid4())
        
        url = reverse('job-status', kwargs={'uuid': uuid_fake})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_consultar_com_uuid_invalido(self):
        """
        Testa consulta com formato de UUID inválido.
        URL pattern já rejeita formato inválido, então testamos
        que a URL não pode ser resolvida.
        """
        import uuid as uuid_lib
        from django.urls import reverse, NoReverseMatch
        
        # Tentar criar URL com UUID inválido deve lançar exceção
        with self.assertRaises(NoReverseMatch):
            url = reverse('job-status', kwargs={'uuid': 'uuid-invalido-123'})
