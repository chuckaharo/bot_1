from telegram import Bot
from src.bot.config import Config
import logging

config = Config()
logger = logging.getLogger(__name__)

async def notify_admins(bot: Bot, message: str) -> None:
    """
    Отправляет уведомление всем администраторам из списка.
    
    Args:
        bot: Объект бота Telegram
        message: Текст уведомления
    """
    try:
        if not config.admin_ids:
            logger.error("Список администраторов пуст")
            return

        for admin_id in config.admin_ids:
            await bot.send_message(
                chat_id=admin_id,
                text=f"🔔 **Уведомление**\n{message}",
                parse_mode="Markdown"
            )
        logger.info("Уведомления отправлены администраторам")

    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {str(e)}", exc_info=True)

async def notify_new_order(bot: Bot, order_id: int, amount: float, currency: str) -> None:
    """
    Уведомление о новом заказе.
    
    Args:
        bot: Объект бота Telegram
        order_id: ID заказа
        amount: Сумма оплаты
        currency: Валюта (BTC/LTC)
    """
    message = (
        f"🛒 Новый заказ!\n"
        f"• Номер: `#{order_id}`\n"
        f"• Сумма: `{amount} {currency}`"
    )
    await notify_admins(bot, message)

async def notify_payment_received(bot: Bot, order_id: int, tx_hash: str) -> None:
    """
    Уведомление об успешной оплате.
    
    Args:
        bot: Объект бота Telegram
        order_id: ID заказа
        tx_hash: Хеш транзакции
    """
    message = (
        f"✅ Оплата получена!\n"
        f"• Заказ: `#{order_id}`\n"
        f"• Транзакция: `{tx_hash}`"
    )
    await notify_admins(bot, message)

async def notify_critical_error(bot: Bot, error: str) -> None:
    """
    Уведомление о критической ошибке.
    
    Args:
        bot: Объект бота Telegram
        error: Текст ошибки
    """
    message = (
        f"🚨 **Критическая ошибка**\n"
        f"```\n{error}\n```"
    )
    await notify_admins(bot, message)