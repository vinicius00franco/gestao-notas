from rest_framework import generics, views, status
from rest_framework.response import Response
from .models import JobProcessamento
from .serializers import UploadNotaFiscalSerializer, JobProcessamentoSerializer
from .services import ProcessamentoService

class ProcessarNotaFiscalView(views.APIView):
    serializer_class = UploadNotaFiscalSerializer
    permission_classes = []  # Temporário para teste

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        service = ProcessamentoService()
        try:
            job = service.criar_job_processamento(
                cnpj=validated_data.get('meu_cnpj'),
                arquivo=validated_data['arquivo']
            )
            return Response({
                "uuid": str(job.uuid),
                "status": {"codigo": job.status.codigo, "descricao": job.status.descricao}
            }, status=status.HTTP_202_ACCEPTED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JobStatusView(generics.RetrieveAPIView):
    queryset = JobProcessamento.objects.all()
    serializer_class = JobProcessamentoSerializer
    lookup_field = 'uuid'
    permission_classes = []  # Temporário para teste