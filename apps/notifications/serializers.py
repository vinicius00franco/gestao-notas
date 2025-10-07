from rest_framework import serializers
from .models import Device
from .models import Notification


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['uuid', 'token', 'platform', 'user', 'empresa', 'active']
        read_only_fields = ['uuid', 'user', 'empresa', 'active']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['uuid', 'user', 'title', 'body', 'data', 'delivered', 'created_at', 'delivered_at']
        read_only_fields = ['uuid', 'delivered', 'created_at', 'delivered_at']
