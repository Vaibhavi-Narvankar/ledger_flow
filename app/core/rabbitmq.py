import aio_pika
from aio_pika import RobustConnection, RobustChannel

from app.core.config import get_settings


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

        await self.channel.declare_queue(
              "ledgerflow.events",
              durable=True,
          )