from celery import Celery
from kombu import Exchange, Queue
from src.config import settings

celery_app = Celery(
    "your_project",
    broker=settings.rabbit.get_rabbitmq_url(),
    backend="rpc://",
    include=[
        "src.tasks.email_verification",
        "src.tasks.user_verification",
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
        "user_authentication": {
            "exchange": "user_authentication",
            "routing_key": "user_authentication",
        },
        "email_verification": {
            "exchange": "email_verification",
            "routing_key": "email_verification",
        },
    },
)

if __name__ == "__main__":
    celery_app.start()
