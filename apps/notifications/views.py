from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Device
from .serializers import DeviceSerializer
from .models import Notification
from .serializers import NotificationSerializer
from django.utils import timezone



class RegisterDeviceView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        platform = request.data.get('platform')
        if not token:
            return Response({'detail': 'token is required'}, status=status.HTTP_400_BAD_REQUEST)

        device, created = Device.objects.update_or_create(
            token=token,
            defaults={'platform': platform, 'active': True},
        )

        # Optionally link to authenticated user and empresa
        if request.user and getattr(request.user, 'is_authenticated', False):
            # Only attach a Django User if present
            if hasattr(request.user, 'id'):
                device.user = request.user
            # Attach empresa if available (EmpresaPrincipal or request.user with property)
            try:
                device.empresa = request.user.minhaempresa
            except Exception:
                pass
            device.save()

        return Response(DeviceSerializer(device).data)


class PendingNotificationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # If authenticated via standard user, filter by that user
        if getattr(request.user, 'is_authenticated', False) and hasattr(request.user, 'id'):
            qs = Notification.objects.filter(user=request.user, delivered=False).order_by('created_at')
            return Response(NotificationSerializer(qs, many=True).data)

        # Empresa principal (custom auth) or anonymous device polling: accept device token
        device_token = request.query_params.get('device') or request.headers.get('X-Device-Token')
        if not device_token:
            return Response({'detail': 'device token required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            device = Device.objects.get(token=device_token, active=True)
        except Device.DoesNotExist:
            return Response({'detail': 'device not found'}, status=status.HTTP_404_NOT_FOUND)
        if not device.user_id:
            return Response([], status=status.HTTP_200_OK)
        qs = Notification.objects.filter(user_id=device.user_id, delivered=False).order_by('created_at')
        return Response(NotificationSerializer(qs, many=True).data)


class AcknowledgeNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        notification_uuid = request.data.get('uuid')
        if not notification_uuid:
            return Response({'detail': 'uuid required'}, status=status.HTTP_400_BAD_REQUEST)

        # Standard user
        if getattr(request.user, 'is_authenticated', False) and hasattr(request.user, 'id'):
            try:
                notif = Notification.objects.get(uuid=notification_uuid, user=request.user)
            except Notification.DoesNotExist:
                return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Empresa/device-based ack
            device_token = request.data.get('device') or request.headers.get('X-Device-Token')
            if not device_token:
                return Response({'detail': 'device token required'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                device = Device.objects.get(token=device_token, active=True)
            except Device.DoesNotExist:
                return Response({'detail': 'device not found'}, status=status.HTTP_404_NOT_FOUND)
            if not device.user_id:
                return Response({'detail': 'device not linked'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                notif = Notification.objects.get(uuid=notification_uuid, user_id=device.user_id)
            except Notification.DoesNotExist:
                return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        notif.delivered = True
        notif.delivered_at = timezone.now()
        notif.save(update_fields=['delivered', 'delivered_at'])
        return Response({'ok': True})
