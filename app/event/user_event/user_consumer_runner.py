import asyncio
from aio_pika import connect_robust
from app.common.config import settings
from app.common.logger import logger
from app.event.user_event.user_consumer_handler import handle_user_deleted


async def consume_user_deleted_events():
    conn = await connect_robust(settings.RABBITMQ_URL)
    channel = await conn.channel()
    exchange = await channel.declare_exchange("user.events", durable=True)

    queue = await channel.declare_queue("user.deleted.queue", durable=True)
    await queue.bind(exchange, routing_key="user.deleted")

    logger.info("[CONSUMER] 사용자 탈퇴 큐 연결됨. 대기 중...")
    await queue.consume(handle_user_deleted)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_user_deleted_events())
    loop.run_forever()


if __name__ == "__main__":
    main()
