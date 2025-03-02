import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional
from src.bot.config import Config
import sys

config = Config()

def setup_logging() -> None:
    """Инициализация системы логирования с ротацией файлов"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True, parents=True)
    
    log_file = logs_dir / f"bot_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Формат логов: [Время] [Уровень] [Модуль] - Сообщение
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Настройка ротации: 5 файлов по 5 МБ каждый
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    # Консольный вывод для DEBUG-режима
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Уровень логирования из конфига
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler],
        force=True  # Перезаписать существующие обработчики
    )

def log_command(user_id: int, command: str, args: Optional[str] = None) -> None:
    """Логирование команд пользователя"""
    try:
        message = f"USER:{user_id} > /{command}"
        if args:
            message += f" {args}"
        logging.info(message)
    except Exception as e:
        logging.error(f"Command log error: {str(e)}", exc_info=True)

def log_admin_action(user_id: int, action: str) -> None:
    """Логирование действий администратора"""
    try:
        logging.warning(
            f"ADMIN ACTION | User:{user_id} | Action: {action}",
            extra={"user_id": user_id}
        )
    except Exception as e:
        logging.error(f"Admin action log error: {str(e)}", exc_info=True)

def log_error(error: str, context: Optional[dict] = None) -> None:
    """Логирование ошибок с контекстом"""
    try:
        log_message = f"ERROR: {error}"
        if context:
            log_message += f" | Context: {context}"
        logging.error(log_message, exc_info=True, stack_info=True)
    except Exception as e:
        logging.critical(f"Error logging failure: {str(e)}", exc_info=True)

def log_critical(event: str, details: Optional[dict] = None) -> None:
    """Логирование критических событий"""
    try:
        log_message = f"CRITICAL: {event}"
        if details:
            log_message += f" | Details: {details}"
        logging.critical(log_message, exc_info=True, stack_info=True)
    except Exception as e:
        print(f"FATAL LOG FAILURE: {str(e)}")  # Fallback