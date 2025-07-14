from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = "DB_USER"
    DB_PASSWORD: str = "DB_PASSWORD"
    DB_HOST: str = "DB_HOST"
    DB_PORT: int = 5432
    DB_NAME: str = "DB_NAME"
    DB_ECHO: bool = False

    JWT_SECRET_KEY: str = "JWT_SECRET_KEY"

    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    RABBITMQ_URL: str = "RABBITMQ_URL"

    REDIS_HOST: str = "REDIS_HOST"
    REDIS_PORT: int = 6379

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env.dev"

settings = Settings()
