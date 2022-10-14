from celery import Celery

from core.config import settings


celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND

celery.conf.update(
    task_track_started=True,
    include=["tickets_processor.services.tickets"],
    timezone='America/Sao_Paulo',
    enable_utc=True,
)


if __name__ == '__main__':
    celery.start()
