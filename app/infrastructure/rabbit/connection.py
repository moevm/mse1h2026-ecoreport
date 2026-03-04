import os
import aio_pika


class RabbitConnectionManager:
    """
    Класс для управления подключением к RabbitMQ.

    Обеспечивает установку надежного соединения и создание каналов.
    """
    def __init__(self):
        """
        Инициализирует менеджер соединения.
        Настройки хоста и порта по умолчанию: localhost:5672.
        """
        self.__host:str = os.getenv("RABBITMQ_HOST", "localhost")
        self.__port:int = 5672
        self._connection:aio_pika.abc.AbstractRobustConnection | None = None

    async def connect(self) -> None:
        """
        Устанавливает отказоустойчивое соединение с брокером сообщений.
        """
        self._connection = await aio_pika.connect_robust(host=self.__host, port=self.__port)

    async def get_channel(self) -> aio_pika.abc.AbstractRobustChannel:
        """
        Создает и возвращает новый канал в рамках текущего соединения.

        :return: Объект канала aio_pika.
        """
        return await self._connection.channel()

    async def close(self) -> None:
        """
        Закрывает текущее соединение с брокером.
        """
        await self._connection.close()