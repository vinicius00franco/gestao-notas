from rest_framework.views import APIView
from rest_framework.response import Response
from prometheus_client import Counter
import logging

mobile_screen_views = Counter(
    'mobile_screen_views_total',
    'Total mobile screen views',
    ['screen', 'platform']
)

mobile_user_actions = Counter(
    'mobile_user_actions_total',
    'Total mobile user actions',
    ['screen', 'action']
)

logger = logging.getLogger(__name__)

class MobileMetricsView(APIView):
    permission_classes = [] # Open endpoint for now

    def post(self, request):
        data = request.data
        screen = data.get('screen')
        action = data.get('user_action')

        # Registrar métricas
        mobile_screen_views.labels(
            screen=screen,
            platform='react_native'
        ).inc()

        if action:
            mobile_user_actions.labels(
                screen=screen,
                action=action
            ).inc()

        # Log estruturado
        logger.info("Mobile metric received", extra={
            'screen': screen,
            'action': action,
            'timestamp': data.get('timestamp'),
            'metric_type': 'mobile_analytics'
        })

        return Response({'status': 'ok'})