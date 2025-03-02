from .commands import register_commands
from .admin import register_admin_handlers
from .payments import register_payment_handlers

def register_handlers(application):
    """Регистрация всех обработчиков команд и callback-ов"""
    register_commands(application)
    register_admin_handlers(application)
    register_payment_handlers(application)