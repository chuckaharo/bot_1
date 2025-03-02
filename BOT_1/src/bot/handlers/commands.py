from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy.orm import Session
from src.bot.database import Product
from src.bot.config import Config
from src.bot.logger import log_command, log_error, log_admin_action

config = Config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        user_id = update.effective_user.id
        log_command(user_id, "/start")
        
        await update.message.reply_text(
            "👋 *Добро пожаловать в CryptoBot!*\n\n"
            "🛍️ Используйте /products для просмотра товаров\n"
            "💳 Для покупки выберите товар и нажмите /pay_[ID]",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        log_error(f"Ошибка команды /start: {str(e)}")
        await update.message.reply_text("❌ Произошла ошибка")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    try:
        user_id = update.effective_user.id
        log_command(user_id, "/help")
        
        help_text = (
            "📖 *Справка по командам:*\n\n"
            "/start - Перезапустить бота\n"
            "/products - Список товаров\n"
            "/help - Показать справку\n"
            "/my_orders - Ваши заказы\n"
            "/support - Техническая поддержка"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
        
    except Exception as e:
        log_error(f"Ошибка команды /help: {str(e)}")

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /products"""
    session = None
    try:
        user_id = update.effective_user.id
        log_command(user_id, "/products")
        
        Session = context.bot_data['session_factory']
        session = Session()
        
        products = session.query(Product).filter(Product.stock > 0).all()
        
        if not products:
            await update.message.reply_text("😔 Товары временно отсутствуют")
            return

        response = ["🛒 *Доступные товары:*\n"]
        for product in products:
            response.append(
                f"▪️ *{product.name}*\n"
                f"   Цена: `{product.price_btc:.8f} ₿` / `{product.price_ltc:.8f} Ł`\n"
                f"   Остаток: {product.stock} шт.\n"
                f"   Купить: /pay_{product.id}"
            )
            
        await update.message.reply_text("\n".join(response), parse_mode="Markdown")
        
    except Exception as e:
        log_error(f"Ошибка команды /products: {str(e)}")
        await update.message.reply_text("❌ Ошибка загрузки товаров")
    finally:
        if session:
            session.close()

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /my_orders"""
    session = None
    try:
        user_id = update.effective_user.id
        log_command(user_id, "/my_orders")
        
        Session = context.bot_data['session_factory']
        session = Session()
        
        orders = session.query(Transaction)\
            .filter(Transaction.user_id == user_id)\
            .order_by(Transaction.created_at.desc())\
            .limit(5)\
            .all()
            
        if not orders:
            await update.message.reply_text("📭 У вас нет активных заказов")
            return
            
        response = ["📋 *Ваши последние заказы:*\n"]
        for order in orders:
            status_emoji = "✅" if order.status == "completed" else "🕒"
            response.append(
                f"{status_emoji} Заказ #{order.id}\n"
                f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"Статус: {order.status.capitalize()}\n"
            )
            
        await update.message.reply_text("\n".join(response), parse_mode="Markdown")
        
    except Exception as e:
        log_error(f"Ошибка команды /my_orders: {str(e)}")
        await update.message.reply_text("❌ Ошибка загрузки заказов")
    finally:
        if session:
            session.close()

def register_commands(application):
    """Регистрация обработчиков команд"""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("products", list_products))
    application.add_handler(CommandHandler("my_orders", my_orders))