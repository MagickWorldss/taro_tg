"""
Модуль с обработчиками
"""
from aiogram import Dispatcher
import logging

logger = logging.getLogger(__name__)


def register_all_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Здесь будут регистрироваться дополнительные handlers
    logger.info("Все обработчики зарегистрированы")

