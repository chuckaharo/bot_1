import os
import logging
import asyncio  # Добавлен импорт asyncio
from telegram import Update  # Добавлен импорт Update
from telegram.ext import Application
from src.bot.config import Config
from src.bot.database import init_db
from src.bot.handlers import register_handlers
from src.bot.logger import setup_logging
from src.bot.notifications import notify_critical_error

# Основные изменения:
# 1. main() стала асинхронной
# 2. Добавлен asyncio.run() для запуска
# 3. Обработка случая, когда application не определена
# 4. Исправлен импорт Update

async def main():
    """Точка входа в приложение"""
    setup_logging()
    logging.info("Запуск бота...")

    application = None  # Для безопасного использования в блоке except
    
    try:
        config = Config()
        logging.info("Конфигурация загружена")

        SessionFactory = init_db(config.database_url)
        logging.info("База данных подключена")

        # Создание приложения
        application = Application.builder() \
            .token(config.bot_token) \
            .post_init(post_init) \
            .build()

        application.bot_data.update({
            "session_factory": SessionFactory,
            "config": config
        })

        register_handlers(application)
        logging.info("Обработчики зарегистрированы")

        # Асинхронный запуск
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

    except Exception as e:
        logging.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
        if application and application.bot:
            # Вызов асинхронной функции через задачу
            asyncio.create_task(notify_critical_error(application.bot, str(e)))
        raise

async def post_init(app: Application) -> None:
    """Пост-инициализация приложения"""
    try:
        await app.bot.set_my_commands([
            ("start", "Главное меню"),
            ("products", "Каталог товаров"),
            ("help", "Помощь по боту")
        ])
        logging.info("Команды бота обновлены")

        await app.bot.send_message(
            chat_id=Config().admin_ids[0],
            text="🟢 Бот успешно запущен!"
        )
    except Exception as e:
        logging.error(f"Ошибка пост-инициализации: {str(e)}")

if __name__ == "__main__":
    # Запуск асинхронного главного метода
    asyncio.run(main())