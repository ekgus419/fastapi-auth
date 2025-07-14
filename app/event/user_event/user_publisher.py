# from app.common.logger import logger  # 공통 로거 사용
#
# async def publish_user_deleted(user_id: int):
#     # 실제로는 RabbitMQ, Kafka 등으로 발행
#     logger.info(f"[QUEUE] 탈퇴 사용자 후처리 이벤트 발행됨: user_id={user_id}")

from aio_pika import Message
from app.event.queue_config import get_connection
from app.common.logger import logger
import json

async def publish_user_deleted(user_id: int):
    conn = await get_connection()
    channel = await conn.channel()

    exchange = await channel.declare_exchange("user.events", durable=True)

    body = json.dumps({
        "event": "USER_DELETED",
        "user_id": user_id
    }).encode()

    await exchange.publish(
        Message(body),
        routing_key="user.deleted"
    )

    logger.info(f"[QUEUE] 탈퇴 사용자 이벤트 발행됨: user_id={user_id}")
