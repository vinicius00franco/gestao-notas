from rest_framework import views, status
from rest_framework.response import Response
from . import selectors

class DashboardStatsView(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            "top_5_fornecedores_pendentes": selectors.get_top_fornecedores_pendentes()
        }, status=status.HTTP_200_OK)
