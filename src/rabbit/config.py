from typing import Any, Optional

from faststream.rabbit.fastapi import RabbitRouter
from src.config import settings


class RabbitService:
    """Класс для работы с RabbitMQ через FastStream"""

    def __init__(self):
        rabbit_url = settings.rabbit.url
        self.router = RabbitRouter(rabbit_url)


rabbit_service = RabbitService()
