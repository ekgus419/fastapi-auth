# FastAPI 기반 Python 이미지 사용
FROM python:3.11-slim-bullseye

# postgresql-client 설치
RUN apt-get update && apt-get install -y postgresql-client netcat

COPY scripts/wait-for-postgres.sh /wait-for-postgres.sh
COPY scripts/wait-for-rabbitmq.sh /wait-for-rabbitmq.sh

RUN chmod +x /wait-for-postgres.sh
RUN chmod +x /wait-for-rabbitmq.sh

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . .

# FastAPI 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
