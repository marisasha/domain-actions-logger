from typing import Any, Optional

from faststream.rabbit.fastapi import RabbitRouter
from src.config import settings


class RabbitMQService:
    """Класс для работы с RabbitMQ через FastStream"""

    def __init__(self):
        scheme = "amqps" if settings.rabbit.ssl else "amqp"
        self.rabbit_url = f"{scheme}://{settings.rabbit.user}:{settings.rabbit.password}@{settings.rabbit.host}:{settings.rabbit.port}/{settings.rabbit.vhost}"
        self.router = RabbitRouter(self.rabbit_url)


rabbitmq_service = RabbitMQService()
