"""Celery application configuration."""

from core.settings import postgres_settings, redis_settings, app_settings
from celery import Celery

celery_app = Celery(
    app_settings.app_name,
    broker=redis_settings.dsn,
    backend=postgres_settings.celery_backend_url,
    include=["domain.celery_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=4,
)
