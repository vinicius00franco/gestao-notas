from rest_framework import generics, views, status
from rest_framework.response import Response
from .models import JobProcessamento
from .serializers import UploadNotaFiscalSerializer, JobProcessamentoSerializer
from .publishers import CeleryTaskPublisher

class ProcessarNotaFiscalView(views.APIView):
    serializer_class = UploadNotaFiscalSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        job = JobProcessamento.objects.create(
            arquivo_original=validated_data['arquivo'],
            meu_cnpj=validated_data['meu_cnpj']
        )
        CeleryTaskPublisher().publish_processamento_nota(job_id=job.id)
        return Response({"id": job.id, "status": job.status}, status=status.HTTP_202_ACCEPTED)

class JobStatusView(generics.RetrieveAPIView):
    queryset = JobProcessamento.objects.all()
    serializer_class = JobProcessamentoSerializer
    lookup_field = 'id'
