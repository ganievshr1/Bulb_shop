from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://admin_user:admin_pass@admin-db:5432/admin_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # Service
    SERVICE_NAME: str = "admin-service"
    SERVICE_PORT: int = 8083
    LOG_LEVEL: str = "INFO"

    # ✅ JWT — секрет через .env или генерируется автоматически
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)  # Автогенерация если нет .env
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # ✅ Уменьшено с 480 до 30 минут!

    # Other services
    PRODUCT_SERVICE_URL: str = "http://product-service:8081/api/v1"
    ORDER_SERVICE_URL: str = "http://order-service:8082/api/v1"

    # ✅ Admin credentials — ТОЛЬКО для инициализации, не для проверки
    ADMIN_LOGIN: str = "admin"
    ADMIN_PASSWORD: str = ""  # Пустой — будет ошибка при старте
    ADMIN_EMAIL: str = "admin@bulbshop.com"
    ADMIN_FULL_NAME: str = "Администратор"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()

    # ✅ Проверка при запуске
    if not settings.ADMIN_PASSWORD:
        raise ValueError(
            "ADMIN_PASSWORD не задан! Создайте .env файл:\n"
            "ADMIN_PASSWORD=your_secure_password_here\n"
            "JWT_SECRET_KEY=your_random_secret_key"
        )

    return settings


settings = get_settings()