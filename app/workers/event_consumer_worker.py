import asyncio
import json
import logging

import aio_pika

from app.core.database import AsyncSessionLocal
from app.core.rabbitmq import RabbitMQService
from app.services.event_consumer import EventConsumer

logger = logging.getLogger(__name__)

QUEUE_NAME = "ledgerflow.events"
RETRY_QUEUE = "ledgerflow.events.retry"

MAX_ATTEMPTS = 3
RETRY_COUNT_HEADER = "x-retry-count"


async def handle_message(
    message: aio_pika.abc.AbstractIncomingMessage,
    consumer: EventConsumer,
) -> None:
    try:
        payload = json.loads(message.body)

        if not isinstance(payload, dict):
            raise ValueError("Message payload must be a JSON object")

        message_id = message.message_id
        event_type = message.type

        if not message_id or not event_type:
            raise ValueError(
                "Message must include message_id and event_type"
            )

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        logger.exception("Rejecting malformed RabbitMQ message")
        await message.reject(requeue=False)
        return

    try:
        processed = await consumer.process_message(
            message_id=message_id,
            event_type=event_type,
            payload=payload,
        )

        await message.ack()

        logger.info(
            "%s event message_id=%s event_type=%s",
            "Processed" if processed else "Skipped duplicate",
            message_id,
            event_type,
        )

    except Exception:
        headers = dict(message.headers or {})

        try:
            retry_count = int(headers.get(RETRY_COUNT_HEADER, 0))
        except (TypeError, ValueError):
            retry_count = 0

        logger.exception(
            "Event processing failed: message_id=%s attempt=%s",
            message_id,
            retry_count + 1,
        )

        if retry_count < MAX_ATTEMPTS - 1:
            headers[RETRY_COUNT_HEADER] = retry_count + 1

            retry_message = aio_pika.Message(
                body=message.body,
                content_type=message.content_type or "application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=message_id,
                type=event_type,
                headers=headers,
            )

            try:
                await message.channel.default_exchange.publish(
                    retry_message,
                    routing_key=RETRY_QUEUE,
                    mandatory=True,
                )

                await message.ack()

                logger.warning(
                    "Scheduled retry %s/%s for message_id=%s",
                    retry_count + 1,
                    MAX_ATTEMPTS - 1,
                    message_id,
                )

            except Exception:
                logger.exception(
                    "Failed to schedule retry; dead-lettering "
                    "message_id=%s",
                    message_id,
                )
                await message.reject(requeue=False)

        else:
            logger.error(
                "Maximum attempts reached; dead-lettering "
                "message_id=%s",
                message_id,
            )
            await message.reject(requeue=False)


async def run_worker() -> None:
    rabbitmq = RabbitMQService()

    try:
        await rabbitmq.connect()
        await rabbitmq.declare_topology()

        if rabbitmq.channel is None:
            raise RuntimeError("RabbitMQ channel is not connected")

        await rabbitmq.channel.set_qos(prefetch_count=10)

        queue = await rabbitmq.channel.declare_queue(
            QUEUE_NAME,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "ledgerflow.events.dlq.exchange",
                "x-dead-letter-routing-key": "ledgerflow.events.dlq",
            },
        )

        consumer = EventConsumer(AsyncSessionLocal)

        logger.info("Event consumer worker started")

        async with queue.iterator() as queue_iterator:
            async for message in queue_iterator:
                await handle_message(message, consumer)

    finally:
        await rabbitmq.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())