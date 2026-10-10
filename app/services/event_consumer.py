import json
import logging
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.processed_event import ProcessedEvent

logger = logging.getLogger(__name__)


class EventConsumer:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session_factory = session_factory

    async def process_message(
        self,
        *,
        message_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> bool:
        async with self.session_factory() as db:
            if not message_id.strip():
               raise ValueError("message_id must not be empty")

            if not event_type.strip():
               raise ValueError("event_type must not be empty")

            if not isinstance(payload, dict):
               raise ValueError("payload must be a JSON object")
            try:
                statement = (
                    insert(ProcessedEvent)
                    .values(
                        message_id=message_id,
                        event_type=event_type,
                    )
                    .on_conflict_do_nothing(
                        index_elements=[ProcessedEvent.message_id]
                    )
                    .returning(ProcessedEvent.message_id)
                )

                result = await db.execute(statement)
                inserted_id = result.scalar_one_or_none()

                if inserted_id is None:
                    await db.rollback()
                    logger.info(
                        "Skipping duplicate event: message_id=%s",
                        message_id,
                    )
                    return False

                # Business event handling will be added in the next step.
                logger.info(
                    "Recorded event: message_id=%s event_type=%s",
                    message_id,
                    event_type,
                )

                await db.commit()
                return True

            except Exception:
                await db.rollback()
                logger.exception(
                    "Failed to process event: message_id=%s",
                    message_id,
                )
                raise


