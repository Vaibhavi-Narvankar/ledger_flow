import asyncio
import json
import logging

import aio_pika
from sqlalchemy.exc import SQLAlchemyError
from collections.abc import Callable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.database import AsyncSessionLocal
from app.core.rabbitmq import RabbitMQService
from app.repositories.outbox import OutboxRepository


logger = logging.getLogger(__name__)

QUEUE_NAME = "ledgerflow.events"
BATCH_SIZE = 100


class OutboxPublisher:
    def __init__(
        self,
        rabbitmq: RabbitMQService,
        session_factory: async_sessionmaker[AsyncSession] = AsyncSessionLocal,
    ) -> None:
        self.rabbitmq = rabbitmq
        self.session_factory = session_factory

    async def publish_pending(self) -> int:
        if self.rabbitmq.channel is None:
            raise RuntimeError("RabbitMQ channel is not connected")

        published_count = 0

        async with self.session_factory() as db:
            try:
                repository = OutboxRepository(db)

                events = await repository.get_pending(
                    limit=BATCH_SIZE,
                )

                for event in events:
                    message = aio_pika.Message(
                        body=json.dumps(event.payload).encode("utf-8"),
                        content_type="application/json",
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        message_id=str(event.id),
                        type=event.event_type,
                    )

                    await self.rabbitmq.channel.default_exchange.publish(
                        message,
                        routing_key=QUEUE_NAME,
                        mandatory=True,
                    )

                    await repository.mark_published(event)
                    published_count += 1

                await db.commit()

            except Exception:
                await db.rollback()
                logger.exception("Failed to publish outbox events")
                raise

        return published_count