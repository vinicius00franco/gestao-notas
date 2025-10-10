from rest_framework import generics, views, status
from rest_framework.response import Response
from .models import JobProcessamento
from .serializers import UploadNotaFiscalSerializer, JobProcessamentoSerializer
from .publishers import CeleryTaskPublisher
from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import get_classifier

class ProcessarNotaFiscalView(views.APIView):
    serializer_class = UploadNotaFiscalSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            empresa = MinhaEmpresa.objects.get(cnpj=validated_data['meu_cnpj'])
        except MinhaEmpresa.DoesNotExist:
            return Response(
                {"detail": "Empresa com CNPJ informado não encontrada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        status_pendente = get_classifier('STATUS_JOB', 'PENDENTE')
        job = JobProcessamento.objects.create(
            arquivo_original=validated_data['arquivo'],
            empresa=empresa,
            status=status_pendente,
        )
        CeleryTaskPublisher().publish_processamento_nota(job_id=job.id)

        return Response({
            "message": "Upload recebido com sucesso. O processamento foi iniciado.",
            "job_uuid": str(job.uuid)
        }, status=status.HTTP_202_ACCEPTED)


class JobStatusView(generics.RetrieveAPIView):
    queryset = JobProcessamento.objects.all()
    serializer_class = JobProcessamentoSerializer
    lookup_field = 'uuid'
