from rest_framework import generics, views, status
from rest_framework.response import Response
import logging
from .models import JobProcessamento
from .serializers import UploadNotaFiscalSerializer, JobProcessamentoSerializer
from .services import ProcessamentoService
from apps.core.metrics import track_route_metrics

logger = logging.getLogger(__name__)

class ProcessarNotaFiscalView(views.APIView):
    serializer_class = UploadNotaFiscalSerializer
    permission_classes = []  # Temporário para teste

    @track_route_metrics
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


class JobStatusView(generics.RetrieveAPIView):
    queryset = JobProcessamento.objects.all()
    serializer_class = JobProcessamentoSerializer
    lookup_field = 'uuid'
    permission_classes = []  # Temporário para teste