from apps.core.observers import Observer
from apps.notifications.models import Notification, Device


class PushStoreObserver(Observer):
    """Creates Notification rows for users when certain events occur.

    This keeps push delivery server-side and lets mobile clients poll pending
    notifications and show them natively.
    """
    def update(self, subject, event_type: str, **kwargs):
        if event_type == 'lancamento_created':
            lanc = kwargs.get('lancamento')
            if lanc is None:
                return
            # Notificar por usuário (id): seleciona usuários a partir de Devices associados à mesma empresa do Job
            try:
                empresa = lanc.nota_fiscal.job_origem.empresa
                device_qs = Device.objects.filter(empresa=empresa, active=True).exclude(user__isnull=True)
                user_ids = set(device_qs.values_list('user_id', flat=True))
                for uid in user_ids:
                    Notification.objects.create(
                        user_id=uid,
                        title='Novo lançamento',
                        body=f"{lanc.descricao} - R$ {lanc.valor}",
                        data={'lancamento_id': str(lanc.uuid)},
                    )
            except Exception:
                # caso o relacionamento não exista ou falhe, não interrompa o fluxo do serviço
                return

        if event_type == 'parceiro_created_or_updated':
            parceiro = kwargs.get('parceiro')
            if parceiro is None:
                return
            # notify admin users or company users (project-specific decision)
            # For now we do nothing specific to keep minimal.
            return
