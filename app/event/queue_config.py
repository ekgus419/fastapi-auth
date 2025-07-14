from typing import Optional

from aio_pika import connect_robust, RobustConnection

from app.common.config import settings

RABBITMQ_URL = settings.RABBITMQ_URL

_connection: Optional[RobustConnection] = None

async def get_connection():
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await connect_robust(RABBITMQ_URL)
    return _connection
