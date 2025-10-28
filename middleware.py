"""
Middleware для бота
"""
from aiogram import Dispatcher
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_middleware(dp: Dispatcher):
    """Настройка middleware"""
    logger.info("Middleware настроен")


class LoggingMiddleware:
    """Middleware для логирования"""
    
    async def __call__(self, handler, event, data):
        """Логирование событий"""
        logger.info(f"Получено событие: {event}")
        return await handler(event, data)

