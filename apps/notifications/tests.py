"""
Testes para o app notifications.
Testa registro de dispositivos, listagem de notificações pendentes e acknowledgement.
"""
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from apps.notifications.models import Device, Notification
from apps.empresa.models import MinhaEmpresa


class RegisterDeviceTestCase(APITestCase):
    """
    Testes para o endpoint de registro de dispositivos.
    Deve permitir registro de dispositivos móveis para notificações.
    RN012: Deve retornar UUID, não ID numérico.
    """

    def test_registrar_dispositivo_sucesso(self):
        """Testa registro de novo dispositivo com token válido."""
        url = reverse('notifications:register-device')
        data = {
            'token': 'ExponentPushToken[xxxxxxxxxxxxxx]',
            'platform': 'ios'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # RN012: Deve retornar UUID
        self.assertIn('uuid', response.data)
        self.assertNotIn('id', response.data)
        
        # Verifica que dispositivo foi criado
        self.assertTrue(Device.objects.filter(token=data['token']).exists())
        device = Device.objects.get(token=data['token'])
        self.assertEqual(device.platform, 'ios')
        self.assertTrue(device.active)

    def test_registrar_dispositivo_android(self):
        """Testa registro de dispositivo Android."""
        url = reverse('notifications:register-device')
        data = {
            'token': 'android-fcm-token-123456',
            'platform': 'android'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        device = Device.objects.get(token=data['token'])
        self.assertEqual(device.platform, 'android')

    def test_atualizar_dispositivo_existente(self):
        """Testa que dispositivo existente é atualizado (não duplicado)."""
        token = 'existing-token-123'
        
        # Cria dispositivo inativo
        Device.objects.create(token=token, platform='ios', active=False)
        
        url = reverse('notifications:register-device')
        data = {
            'token': token,
            'platform': 'android'  # Mudando plataforma
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve ter apenas 1 dispositivo (atualizado, não duplicado)
        self.assertEqual(Device.objects.filter(token=token).count(), 1)
        
        device = Device.objects.get(token=token)
        self.assertEqual(device.platform, 'android')
        self.assertTrue(device.active)  # Deve reativar

    def test_registrar_sem_token(self):
        """Testa validação de token obrigatório."""
        url = reverse('notifications:register-device')
        data = {
            'platform': 'ios'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vincular_dispositivo_a_usuario_autenticado(self):
        """Testa que dispositivo é vinculado a usuário autenticado."""
        # Cria usuário e autentica
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=user)
        
        url = reverse('notifications:register-device')
        data = {
            'token': 'user-device-token',
            'platform': 'ios'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        device = Device.objects.get(token=data['token'])
        self.assertEqual(device.user, user)


class PendingNotificationsTestCase(APITestCase):
    """
    Testes para o endpoint de listagem de notificações pendentes.
    Deve retornar notificações não entregues para o usuário.
    RN012: Deve retornar UUID, não ID numérico.
    """

    def setUp(self):
        """Prepara dados iniciais para os testes."""
        # Cria usuário
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Cria dispositivo vinculado ao usuário
        self.device = Device.objects.create(
            user=self.user,
            token='test-device-token',
            platform='ios',
            active=True
        )

    def test_listar_notificacoes_pendentes_autenticado(self):
        """Testa listagem de notificações para usuário autenticado."""
        # Cria notificações pendentes
        notif1 = Notification.objects.create(
            user=self.user,
            title='Notificação 1',
            body='Corpo da notificação 1',
            delivered=False
        )
        
        notif2 = Notification.objects.create(
            user=self.user,
            title='Notificação 2',
            body='Corpo da notificação 2',
            delivered=False
        )
        
        # Cria notificação já entregue (não deve aparecer)
        notif3 = Notification.objects.create(
            user=self.user,
            title='Notificação Entregue',
            body='Já foi entregue',
            delivered=True
        )
        
        # Autentica usuário
        self.client.force_authenticate(user=self.user)
        
        url = reverse('notifications:pending')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve retornar apenas 2 notificações pendentes
        self.assertEqual(len(response.data), 2)
        
        # RN012: Deve retornar UUID, não ID
        self.assertIn('uuid', response.data[0])
        self.assertNotIn('id', response.data[0])
        
        # Verifica dados das notificações
        titulos = [n['title'] for n in response.data]
        self.assertIn('Notificação 1', titulos)
        self.assertIn('Notificação 2', titulos)
        self.assertNotIn('Notificação Entregue', titulos)

    def test_listar_notificacoes_com_device_token(self):
        """Testa listagem de notificações usando device token (não autenticado)."""
        # Cria notificação
        Notification.objects.create(
            user=self.user,
            title='Notificação Device',
            body='Corpo notificação device',
            delivered=False
        )
        
        url = reverse('notifications:pending')
        response = self.client.get(url, {'device': self.device.token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Notificação Device')

    def test_nao_listar_notificacoes_de_outros_usuarios(self):
        """Testa que não retorna notificações de outros usuários."""
        # Cria outro usuário
        outro_user = User.objects.create_user(username='otheruser', password='otherpass')
        
        # Cria notificação para outro usuário
        Notification.objects.create(
            user=outro_user,
            title='Notificação de Outro',
            body='Não deve aparecer',
            delivered=False
        )
        
        # Autentica como primeiro usuário
        self.client.force_authenticate(user=self.user)
        
        url = reverse('notifications:pending')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Não deve retornar notificação de outro usuário
        self.assertEqual(len(response.data), 0)

    def test_sem_autenticacao_e_sem_device_token(self):
        """
        Testa que retorna erro se não autenticado e sem device token.
        Agora que a view aceita AllowAny, verifica lógica interna.
        """
        url = reverse('notifications:pending')
        response = self.client.get(url)

        # View retorna 400 porque não há usuário autenticado nem device token
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AcknowledgeNotificationTestCase(APITestCase):
    """
    Testes para o endpoint de confirmação de entrega de notificação.
    Deve marcar notificação como entregue usando UUID.
    RN012: Deve aceitar UUID, não ID numérico.
    """

    def setUp(self):
        """Prepara dados iniciais para os testes."""
        # Cria usuário
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Cria dispositivo
        self.device = Device.objects.create(
            user=self.user,
            token='test-device-token',
            platform='ios',
            active=True
        )
        
        # Cria notificação pendente
        self.notification = Notification.objects.create(
            user=self.user,
            title='Notificação Teste',
            body='Corpo da notificação',
            delivered=False
        )

    def test_confirmar_notificacao_com_usuario_autenticado(self):
        """
        RN012: Testa confirmação de notificação usando UUID.
        Deve marcar como entregue e registrar timestamp.
        """
        self.client.force_authenticate(user=self.user)
        
        url = reverse('notifications:ack')
        data = {
            'uuid': str(self.notification.uuid)  # Usa UUID, não ID
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ok'], True)
        
        # Verifica que notificação foi marcada como entregue
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.delivered)
        self.assertIsNotNone(self.notification.delivered_at)

    def test_confirmar_notificacao_com_device_token(self):
        """Testa confirmação usando device token (não autenticado)."""
        url = reverse('notifications:ack')
        data = {
            'uuid': str(self.notification.uuid),
            'device': self.device.token
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.delivered)

    def test_confirmar_sem_uuid(self):
        """Testa validação de UUID obrigatório."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('notifications:ack')
        data = {}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirmar_notificacao_inexistente(self):
        """Testa confirmação de notificação que não existe."""
        import uuid
        
        self.client.force_authenticate(user=self.user)
        
        url = reverse('notifications:ack')
        data = {
            'uuid': str(uuid.uuid4())  # UUID que não existe
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirmar_notificacao_de_outro_usuario(self):
        """Testa que não pode confirmar notificação de outro usuário."""
        # Cria outro usuário e notificação
        outro_user = User.objects.create_user(username='otheruser', password='otherpass')
        notif_outro = Notification.objects.create(
            user=outro_user,
            title='Notificação de Outro',
            body='Não deve poder confirmar',
            delivered=False
        )
        
        # Autentica como primeiro usuário
        self.client.force_authenticate(user=self.user)
        
        url = reverse('notifications:ack')
        data = {
            'uuid': str(notif_outro.uuid)
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Notificação não deve ter sido marcada como entregue
        notif_outro.refresh_from_db()
        self.assertFalse(notif_outro.delivered)
