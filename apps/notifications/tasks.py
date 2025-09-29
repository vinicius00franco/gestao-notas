from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_push_to_tokens(self, tokens: list, payload: dict):
    # Placeholder: actual implementation should call firebase_admin.messaging
    # or FCM HTTP v1. For now we log and pretend to send.
    try:
        logger.info('Sending push to %d tokens: %s', len(tokens), payload)
        # TODO: integrate firebase_admin or HTTP call here
        return {'sent': len(tokens)}
    except Exception as exc:
        logger.exception('Error sending push')
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
