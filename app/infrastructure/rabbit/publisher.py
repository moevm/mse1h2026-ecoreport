import json
import logging
from typing import Optional
import aio_pika
import aiormq

logger = logging.getLogger("uvicorn")


class RabbitPublisher:
    """
    Класс для публикации сообщений в RabbitMQ.
    """
    def __init__(self, exchange:aio_pika.abc.AbstractRobustExchange):
        """
        Инициализирует издателя.

        :param exchange: Точка обмена (Exchange), в которую будут публиковаться сообщения.
        """
        self._exchange = exchange

    async def publish_direct(self, routing_key:str, body: dict) -> Optional[aiormq.abc.ConfirmationFrameType]:
        """
        Публикует сообщение в RabbitMQ с использованием прямого роутинга.

        :param routing_key: Ключ маршрутизации.
        :param body: Словарь с данными сообщения (будет сериализован в JSON).
        :return: Ответ о подтверждении доставки от RabbitMQ.
        """
        wrapped_message = aio_pika.Message(json.dumps(body).encode(),
                                           delivery_mode=aio_pika.DeliveryMode.PERSISTENT)
        logger.info(f"Отправка сообщения с routing key: {routing_key}")
        return await self._exchange.publish(message=wrapped_message, routing_key=routing_key)

