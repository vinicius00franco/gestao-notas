from rest_framework import generics, views, status
from rest_framework.response import Response
import logging
from .models import JobProcessamento
from .serializers import UploadNotaFiscalSerializer, JobProcessamentoSerializer
from .services import ProcessamentoService
from .models import JobProcessamento
from apps.classificadores.models import get_classifier
from .tasks import processar_nota_fiscal_task

logger = logging.getLogger(__name__)

class ProcessarNotaFiscalView(views.APIView):
    serializer_class = UploadNotaFiscalSerializer
    permission_classes = []  # Temporário para teste

    def post(self, request, *args, **kwargs):
        logger.info("API: Recebida requisição POST para processar nota fiscal")
        logger.debug(f"API: Headers: {dict(request.headers)}")
        logger.debug(f"API: Data keys: {list(request.data.keys()) if hasattr(request.data, 'keys') else 'No data'}")

        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            logger.info("API: Dados validados com sucesso")
            logger.debug(f"API: Dados validados: CNPJ={validated_data.get('meu_cnpj')}, Arquivo={validated_data.get('arquivo').name if validated_data.get('arquivo') else 'None'}")
        except Exception as e:
            logger.error(f"API: Erro na validação dos dados: {str(e)}")
            raise

        service = ProcessamentoService()
        try:
            logger.info("API: Chamando serviço de processamento")
            job = service.criar_job_processamento(
                cnpj=validated_data.get('meu_cnpj'),
                arquivo=validated_data['arquivo']
            )
            logger.info(f"API: Job criado com sucesso - UUID: {job.uuid}")
            response_data = {
                "uuid": str(job.uuid),
                "status": {"codigo": job.status.codigo, "descricao": job.status.descricao}
            }
            logger.debug(f"API: Resposta: {response_data}")
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        except ValueError as e:
            logger.warning(f"API: Erro de validação no processamento: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"API: Erro inesperado no processamento: {str(e)}", exc_info=True)
            return Response({"detail": "Erro interno do servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobStatusView(generics.RetrieveDestroyAPIView):
    """
    Recupera o status do job (GET) e permite remoção do job (DELETE).
    """
    queryset = JobProcessamento.objects.all()
    serializer_class = JobProcessamentoSerializer
    lookup_field = 'uuid'
    permission_classes = []  # Temporário para teste

    def delete(self, request, *args, **kwargs):
        """Remove o job do sistema. Isso também removerá o arquivo submetido.

        Retorna 204 No Content em caso de sucesso.
        """
        instance = self.get_object()
        # Não permitir remover um job em processamento
        current_status = instance.status.codigo if instance.status else None
        if current_status == 'PROCESSANDO':
            return Response({'detail': 'Job em processamento não pode ser excluído'}, status=status.HTTP_409_CONFLICT)

        # Remover arquivo físico se presente
        try:
            if instance.arquivo_original:
                instance.arquivo_original.delete(save=False)
        except Exception:
            logger.exception('Falha ao remover arquivo do job %s', instance.uuid)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def post(self, request, *args, **kwargs):
        """Enfileira processamento para o job atual (POST on /api/jobs/<uuid>/).

        Se o job estiver em processamento, retorna 409. Caso contrário reseta o
        status para PENDENTE, limpa mensagem_erro/dt_conclusao e enfileira a
        tarefa Celery para processar o job.
        """
        instance = self.get_object()
        current_status = instance.status.codigo if instance.status else None
        if current_status == 'PROCESSANDO':
            return Response({'detail': 'Job já está em processamento'}, status=status.HTTP_409_CONFLICT)

        # Resetar status e campos auxiliares
        try:
            instance.status = get_classifier('STATUS_JOB', 'PENDENTE')
        except Exception:
            logger.exception('Erro ao obter classificador PENDENTE')
        instance.mensagem_erro = None
        instance.dt_conclusao = None
        instance.save(update_fields=['status', 'mensagem_erro', 'dt_conclusao'])

        try:
            processar_nota_fiscal_task.delay(instance.id)
        except Exception:
            logger.exception('Falha ao enfileirar processamento para job %s', instance.uuid)
            return Response({'detail': 'Falha ao enfileirar processamento'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'uuid': str(instance.uuid), 'status': {'codigo': instance.status.codigo, 'descricao': instance.status.descricao}}, status=status.HTTP_202_ACCEPTED)