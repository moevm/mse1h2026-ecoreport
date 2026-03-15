from typing import AsyncGenerator, Any
import aio_pika
from aio_pika.abc import AbstractIncomingMessage


class RabbitConsumer:
    """
    Класс для потребления сообщений из очередей RabbitMQ.
    """
    def __init__(self, channel:aio_pika.abc.AbstractRobustChannel):
        """
        Инициализирует потребителя.

        :param channel: Канал RabbitMQ для работы.
        """
        self._channel = channel

    async def consume(self, queue_name:str) -> AsyncGenerator[AbstractIncomingMessage, Any]:
        """
        Подписывается на указанную очередь и возвращает генератор сообщений.

        :param queue_name: Имя очереди.
        :return: Асинхронный генератор входящих сообщений.
        """
        queue = await self._channel.declare_queue(name=queue_name, durable=True)

        async with queue.iterator() as q_iter:
            async for msg in q_iter:
                yield msg
