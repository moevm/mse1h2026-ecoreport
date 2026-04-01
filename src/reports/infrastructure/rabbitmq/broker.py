from faststream.rabbit import RabbitBroker
from reports.core.config import settings

broker = RabbitBroker(settings.rabbit_url)