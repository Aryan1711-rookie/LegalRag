import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "legalmind",
    broker=os.environ["CELERY_BROKER_URL"],
    backend=os.environ["CELERY_RESULT_BACKEND"],
    include=["workers.tasks"]
)

celery_app.conf.update(

    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task tracking
    task_track_started=True,
    task_default_queue="legalmind",

    # Worker configuration
    worker_prefetch_multiplier=1,

    # Connection recovery
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,

    # Task execution limits
    task_soft_time_limit=1800,
    task_time_limit=1860,

    # Redis broker configuration
    broker_transport_options={
        "visibility_timeout": 3600
    },

    # Result retention
    result_expires=86400
)