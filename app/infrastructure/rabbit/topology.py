import aio_pika


class ReportsTopology:
    """
    Класс для настройки топологии RabbitMQ (точки обмена, очереди и их привязки).
    """
    EXCHANGE_NAME = "reports"
    GENERATE_QUEUE_NAME = "reports.generate"
    GENERATED_QUEUE_NAME = "reports.generated"

    @classmethod
    async def setup(cls, channel:aio_pika.abc.AbstractRobustChannel) -> aio_pika.abc.AbstractRobustExchange:
        """
        Создает точку обмена и очереди, необходимые для работы системы генерации отчетов,
        и устанавливает связи между ними.

        :param channel: Канал RabbitMQ для настройки.
        :return: Настроенная точка обмена Exchange.
        """
        exchange = await channel.declare_exchange(name=cls.EXCHANGE_NAME,
                                                  type=aio_pika.ExchangeType.DIRECT, durable=True)
        q1 = await channel.declare_queue(name=cls.GENERATE_QUEUE_NAME, durable=True)
        q2 = await channel.declare_queue(name=cls.GENERATED_QUEUE_NAME, durable=True)

        await q1.bind(exchange=exchange, routing_key=cls.GENERATE_QUEUE_NAME)
        await q2.bind(exchange=exchange, routing_key=cls.GENERATED_QUEUE_NAME)

        return exchange
