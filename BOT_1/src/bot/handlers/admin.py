from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from sqlalchemy.orm import Session
from src.bot.database import Product, Transaction
from src.bot.config import Config
from src.bot.notifications import notify_admins
from src.bot.logger import log_admin_action, log_error

config = Config()

def admin_only(func):
    """Декоратор для проверки прав администратора"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in config.admin_ids:
            await update.message.reply_text("🚫 Доступ запрещен!")
            return
        return await func(update, context)
    return wrapper

@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Панель администратора"""
    try:
        keyboard = [
            [InlineKeyboardButton("📦 Управление товарами", callback_data="admin_products")],
            [InlineKeyboardButton("📊 Статистика продаж", callback_data="admin_stats")],
            [InlineKeyboardButton("📝 Последние заказы", callback_data="admin_orders")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ *Панель администратора*:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        log_admin_action(update.effective_user.id, "Открытие панели администратора")
        
    except Exception as e:
        log_error(f"Admin panel error: {str(e)}")
        await notify_admins(context.bot, f"Ошибка панели: {str(e)}")

async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок админки"""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "admin_products":
            await query.edit_message_text(
                "📦 *Управление товарами*\n\n"
                "Используйте команды:\n"
                "/add_product - Добавить товар\n"
                "/update_stock - Изменить количество\n"
                "/products - Список товаров",
                parse_mode="Markdown"
            )
        elif query.data == "admin_stats":
            await show_stats(update, context)
        elif query.data == "admin_orders":
            await show_recent_orders(update, context)
            
    except Exception as e:
        log_error(f"Admin button handler error: {str(e)}")

@admin_only
async def show_recent_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать последние заказы"""
    session = None
    try:
        Session = context.bot_data['session_factory']
        session = Session()
        
        orders = session.query(Transaction)\
            .order_by(Transaction.created_at.desc())\
            .limit(10)\
            .all()
            
        if not orders:
            await update.message.reply_text("📭 Нет последних заказов")
            return
            
        response = ["📋 *Последние 10 заказов:*\n"]
        for order in orders:
            response.append(
                f"#{order.id} {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"Статус: {order.status} | Сумма: {order.amount} {order.currency}"
            )
            
        await update.message.reply_text("\n".join(response), parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text("❌ Ошибка получения заказов")
        log_error(f"Order history error: {str(e)}")
    finally:
        if session:
            session.close()

@admin_only
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление товара"""
    session = None
    try:
        args = context.args
        if len(args) != 5:
            raise ValueError("❌ Формат: /add_product <название> <цена BTC> <цена LTC> <file_id> <количество>")
        
        Session = context.bot_data['session_factory']
        session = Session()
        
        name = args[0]
        price_btc = float(args[1])
        price_ltc = float(args[2])
        file_id = args[3]
        stock = int(args[4])
        
        product = Product(
            name=name,
            price_btc=price_btc,
            price_ltc=price_ltc,
            file_id=file_id,
            stock=stock
        )
        session.add(product)
        session.commit()
        await update.message.reply_text("✅ Товар добавлен")
        log_admin_action(update.effective_user.id, f"Добавлен товар: {name}")
        
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        log_error(f"Add product error: {str(e)}")
    finally:
        if session:
            session.close()

@admin_only
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика продаж"""
    session = None
    try:
        Session = context.bot_data['session_factory']
        session = Session()
        
        total_products = session.query(Product).count()
        total_sales = session.query(Transaction).filter_by(status="completed").count()
        pending_orders = session.query(Transaction).filter_by(status="pending").count()
        
        stats_text = (
            "📊 *Статистика продаж*\n\n"
            f"• Товаров в каталоге: `{total_products}`\n"
            f"• Успешных заказов: `{total_sales}`\n"
            f"• Ожидает оплаты: `{pending_orders}`"
        )
        await update.message.reply_text(stats_text, parse_mode="Markdown")
        log_admin_action(update.effective_user.id, "Просмотр статистики")
        
    except Exception as e:
        await update.message.reply_text("❌ Ошибка получения статистики")
        log_error(f"Stats error: {str(e)}")
    finally:
        if session:
            session.close()

@admin_only
async def update_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновление количества товара"""
    session = None
    try:
        args = context.args
        if len(args) != 2:
            raise ValueError("❌ Формат: /update_stock <ID товара> <новое количество>")
            
        product_id = int(args[0])
        new_stock = int(args[1])
        
        Session = context.bot_data['session_factory']
        session = Session()
        
        product = session.query(Product).get(product_id)
        if product:
            product.stock = new_stock
            session.commit()
            await update.message.reply_text(f"✅ Товар ID {product_id} обновлен")
            log_admin_action(update.effective_user.id, f"Обновлен stock товара #{product_id}")
        else:
            await update.message.reply_text("❌ Товар не найден")
            
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        log_error(f"Update stock error: {str(e)}")
    finally:
        if session:
            session.close()

def register_admin_handlers(application):
    """Регистрация административных обработчиков"""
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_button_handler, pattern="^admin_"))
    application.add_handler(CommandHandler("add_product", add_product))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CommandHandler("update_stock", update_stock))