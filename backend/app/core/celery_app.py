from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "agrivision",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.services.crop_service",
        "app.services.pest_service",
        "app.services.soil_service",
        "app.services.report_service",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    result_expires=3600,
)
