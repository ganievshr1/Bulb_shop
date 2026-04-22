from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://order_user:order_pass@order-db:5432/order_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    SERVICE_NAME: str = "order-service"
    SERVICE_PORT: int = 8082

    PRODUCT_SERVICE_URL: str = "http://product-service:8081/api/v1"

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()