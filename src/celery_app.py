from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from src.config import settings

celery_app = Celery(
    "domain",
    broker=settings.rabbit.url,
    backend="rpc://",
    include=[
        "src.tasks.email_sender",
        "src.tasks.advertising_sheduler",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    task_queues={
        "email_sender": {
            "exchange": "email_sender",
            "routing_key": "email_sender",
        },
        "report": {
            "exchange": "report",
            "routing_key": "report",
        },
    },
    # Настройки для Beat
    beat_schedule={
        "send-report-daily-8pm": {
            "task": "send_report",
            "schedule": crontab(minute="0", hour="20"),
            "options": {"queue": "report"},
        },
    },
    beat_max_loop_interval=30,
    beat_scheduler="celery.beat:PersistentScheduler",
)

if __name__ == "__main__":
    celery_app.start()
