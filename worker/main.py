from celery import Celery

from core.config import settings


celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Brasilia',
    enable_utc=True,
)


if __name__ == '__main__':
    celery.start()
