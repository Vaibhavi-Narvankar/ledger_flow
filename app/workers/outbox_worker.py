import asyncio
import logging

from app.core.rabbitmq import RabbitMQService
from app.services.outbox_publisher import OutboxPublisher

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 2


async def run_worker() -> None:
    rabbitmq = RabbitMQService()

    try:
        await rabbitmq.connect()
        await rabbitmq.declare_topology()

        publisher = OutboxPublisher(rabbitmq)

        logger.info("Outbox publisher worker started")

        while True:
            try:
                published_count = await publisher.publish_pending()

                if published_count:
                    logger.info(
                        "Published %s outbox events",
                        published_count,
                    )

            except Exception:
                logger.exception("Outbox publishing iteration failed")

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    finally:
        await rabbitmq.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())