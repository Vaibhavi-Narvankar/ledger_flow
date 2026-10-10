import aio_pika
from aio_pika import RobustConnection, RobustChannel

from app.core.config import get_settings


EVENTS_QUEUE = "ledgerflow.events"
RETRY_QUEUE = "ledgerflow.events.retry"
DLQ_QUEUE = "ledgerflow.events.dlq"

EVENTS_EXCHANGE = "ledgerflow.events.exchange"
RETRY_EXCHANGE = "ledgerflow.events.retry.exchange"
DLQ_EXCHANGE = "ledgerflow.events.dlq.exchange"

RETRY_DELAY_MS = 5000


class RabbitMQService:
    def __init__(self) -> None:
        self.connection: RobustConnection | None = None
        self.channel: RobustChannel | None = None

    async def connect(self) -> None:
        settings = get_settings()

        self.connection = await aio_pika.connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
        )

        self.channel = await self.connection.channel(
            publisher_confirms=True,
        )

    async def close(self) -> None:
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

        self.connection = None
        self.channel = None

    async def declare_topology(self) -> None:
        if self.channel is None:
            raise RuntimeError("RabbitMQ channel is not connected")

        events_exchange = await self.channel.declare_exchange(
            EVENTS_EXCHANGE,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        retry_exchange = await self.channel.declare_exchange(
            RETRY_EXCHANGE,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        dlq_exchange = await self.channel.declare_exchange(
            DLQ_EXCHANGE,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        # Main queue: rejected messages are routed to the DLQ.
        events_queue = await self.channel.declare_queue(
            EVENTS_QUEUE,
            durable=True,
            arguments={
                "x-dead-letter-exchange": DLQ_EXCHANGE,
                "x-dead-letter-routing-key": DLQ_QUEUE,
            },
        )

        # Retry queue: messages return to the main queue after a delay.
        retry_queue = await self.channel.declare_queue(
            RETRY_QUEUE,
            durable=True,
            arguments={
                "x-message-ttl": RETRY_DELAY_MS,
                "x-dead-letter-exchange": EVENTS_EXCHANGE,
                "x-dead-letter-routing-key": EVENTS_QUEUE,
            },
        )

        # Dead-letter queue: failed messages remain available for inspection.
        dlq_queue = await self.channel.declare_queue(
            DLQ_QUEUE,
            durable=True,
        )

        await events_queue.bind(
            events_exchange,
            routing_key=EVENTS_QUEUE,
        )

        await retry_queue.bind(
            retry_exchange,
            routing_key=RETRY_QUEUE,
        )

        await dlq_queue.bind(
            dlq_exchange,
            routing_key=DLQ_QUEUE,
        )