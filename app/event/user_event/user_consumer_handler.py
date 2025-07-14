import json
from aio_pika import IncomingMessage
from app.common.logger import logger


async def handle_user_deleted(message: IncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            user_id = data.get("user_id")
            logger.info(f"[CONSUMER] 사용자 탈퇴 이벤트 수신: user_id={user_id}")

            # TODO: 실제 후처리 서비스 로직 삽입

        except Exception as e:
            logger.error(f"[CONSUMER] 메시지 처리 실패: {e}")
