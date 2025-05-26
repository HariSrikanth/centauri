from celery import Celery
import structlog

from apps.api.core.config import settings

logger = structlog.get_logger()

# Create Celery app
celery_app = Celery(
    "alpha_me",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=["apps.workers.tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "ingestion": {
            "exchange": "ingestion",
            "routing_key": "ingestion",
        },
        "ai": {
            "exchange": "ai",
            "routing_key": "ai",
        },
    },
)

# Import tasks
from apps.workers.tasks import * 