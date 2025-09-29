from django.db import models
from django.conf import settings


class Device(models.Model):
    PLATFORM_CHOICES = (('ios', 'iOS'), ('android', 'Android'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    empresa = models.ForeignKey('empresa.MinhaEmpresa', null=True, blank=True, on_delete=models.CASCADE)
    token = models.CharField(max_length=512, unique=True)
    platform = models.CharField(max_length=16, choices=PLATFORM_CHOICES, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Device {self.token[:8]}... ({self.platform})"


class Notification(models.Model):
    """Server-side stored notification for a user.

    The mobile client will poll `/api/notifications/pending/` and display these
    as local notifications when appropriate.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(null=True, blank=True)
    delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.user_id}: {self.title[:20]}"
