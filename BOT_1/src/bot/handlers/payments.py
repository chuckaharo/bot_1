from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from src.bot.crypto import CryptoProcessor
from src.bot.database import Transaction, Product
from src.bot.config import Config
from src.bot.handlers.admin import admin_only
import logging

config = Config()
crypto = CryptoProcessor(config.blockcypher_api)
logger = logging.getLogger(__name__)

async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инициализация процесса оплаты"""
    try:
        product_id = int(context.args[0])
        Session = context.bot_data['session']
        
        with Session() as session:
            product = session.query(Product).get(product_id)
            if not product or product.stock < 1:
                await update.message.reply_text("❌ Товар недоступен")
                return

            wallet = crypto.generate_wallet('btc' if product.price_btc > 0 else 'ltc')
            currency = 'BTC' if product.price_btc > 0 else 'LTC'
            amount = product.price_btc if currency == 'BTC' else product.price_ltc

            transaction = Transaction(
                user_id=update.effective_user.id,
                product_id=product.id,
                crypto_address=wallet['address'],
                amount=amount,
                currency=currency,
                status='pending'
            )
            session.add(transaction)
            session.commit()

            keyboard = [[InlineKeyboardButton("✅ Я оплатил", callback_data=f"check_{transaction.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message_text = (
                f"💳 Оплата {product.name}\n\n"
                f"➖➖➖➖➖➖➖➖➖\n"
                f"💰 Сумма: {amount} {currency}\n"
                f"📥 Адрес: {wallet['address']}\n"
                f"➖➖➖➖➖➖➖➖➖\n"
                f"⚠️ Отправьте точную сумму на указанный адрес"
            )

            await update.message.reply_text(message_text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Payment error: {e}")
        await update.message.reply_text("❌ Ошибка при создании платежа")

async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    transaction_id = int(query.data.split('_')[1])
    Session = context.bot_data['session']
    
    try:
        with Session() as session:
            transaction = session.query(Transaction).get(transaction_id)
            if not transaction:
                await query.edit_message_text("❌ Транзакция не найдена")
                return

            if crypto.check_payment(transaction.crypto_address, transaction.currency.lower()):
                transaction.status = 'completed'
                product = session.query(Product).get(transaction.product_id)
                product.stock -= 1
                session.commit()
                
                await query.edit_message_text(
                    "✅ Платеж подтвержден!\n"
                    "📦 Ваш товар будет отправлен в течение 24 часов"
                )
                
                # Уведомление администратора
                admin_text = (
                    f"🛎 Новый платеж!\n\n"
                    f"• Пользователь: @{query.from_user.username}\n"
                    f"• Товар: {product.name}\n"
                    f"• Сумма: {transaction.amount} {transaction.currency}"
                )
                for admin_id in config.admin_ids:
                    await context.bot.send_message(admin_id, admin_text)
            else:
                await query.edit_message_text("⌛️ Платеж еще не получен. Попробуйте проверить позже")

    except Exception as e:
        logger.error(f"Payment check error: {e}")
        await query.edit_message_text("❌ Ошибка при проверке платежа")

@admin_only
async def refund_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат средств по транзакции"""
    try:
        transaction_id = int(context.args[0])
        Session = context.bot_data['session']
        
        with Session() as session:
            transaction = session.query(Transaction).get(transaction_id)
            if transaction and transaction.status == 'completed':
                transaction.status = 'refunded'
                session.commit()
                await update.message.reply_text("✅ Возврат успешно выполнен")
            else:
                await update.message.reply_text("❌ Транзакция не найдена или уже возвращена")

    except Exception as e:
        await update.message.reply_text("❌ Формат: /refund <ID транзакции>")

def register_payment_handlers(application):
    """Регистрация обработчиков платежей"""
    application.add_handler(CommandHandler("pay", start_payment))
    application.add_handler(CallbackQueryHandler(check_payment_callback, pattern="^check_"))
    application.add_handler(CommandHandler("refund", refund_transaction))