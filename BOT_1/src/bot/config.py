import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, Field

# Загрузка переменных из .env
load_dotenv()

class Config(BaseSettings):
    """
    Конфигурация приложения.
    Все параметры автоматически загружаются из переменных окружения или .env файла.
    """
    
    # Telegram
    bot_token: str = Field(..., env="TOKEN")
    admin_ids: List[int] = Field(
        default_factory=lambda: [123456789],  # Пример ID по умолчанию
        description="Список ID администраторов через запятую",
        env="ADMIN_IDS"
    )
    
    # Базы данных
    database_url: AnyUrl = Field(..., env="DATABASE_URL")
    redis_url: AnyUrl = Field(..., env="REDIS_URL")
    
    # Безопасность
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    
    # API
    blockcypher_api: Optional[str] = Field(
        default=None,
        env="BLOCKCYPHER_API",
        description="API-ключ BlockCypher (опционально)"
    )
    
    # Логирование
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Traefik
    traefik_domain: Optional[str] = Field(
        default=None,
        env="DOMAIN",
        description="Домен для Traefik (опционально)"
    )
    traefik_email: Optional[str] = Field(
        default=None,
        env="EMAIL",
        description="Email для сертификатов Let's Encrypt (опционально)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Игнорировать регистр переменных


# Создание экземпляра конфигурации
config = Config()