from rest_framework import serializers
from .models import Device
from .models import Notification


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'token', 'platform', 'user', 'empresa', 'active']
        read_only_fields = ['id', 'user', 'empresa', 'active']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'body', 'data', 'delivered', 'created_at', 'delivered_at']
        read_only_fields = ['id', 'delivered', 'created_at', 'delivered_at']
