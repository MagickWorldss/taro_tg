"""
Модуль админ-панели
"""
import os
import logging
from aiogram import Bot, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, List
from database import Database

logger = logging.getLogger(__name__)

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
db = Database()


async def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return user_id == ADMIN_ID


async def handle_admin_command(message: types.Message, bot: Bot):
    """Обработчик админских команд"""
    if not await is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды")
        return
    
    command = message.text.split()[0] if message.text else ""
    
    if command == "/admin":
        await show_admin_panel(message, bot)
    elif command == "/admin_stats":
        await show_statistics(message, bot)
    elif command == "/admin_users":
        await show_users(message, bot)
    elif command == "/admin_appointments":
        await show_appointments(message, bot)
    elif command == "/admin_slots":
        await show_slots(message, bot)
    elif command == "/admin_news":
        await show_news_panel(message, bot)


async def show_admin_panel(message: types.Message, bot: Bot):
    """Показать админ панель"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="📅 Записи", callback_data="admin_appointments")],
        [InlineKeyboardButton(text="⏰ Управление слотами", callback_data="admin_slots")],
        [InlineKeyboardButton(text="📰 Управление новостями", callback_data="admin_news")],
        [InlineKeyboardButton(text="➕ Добавить слот", callback_data="admin_add_slot")],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    stats = db.get_stats()
    
    await message.answer(
        f"🔧 *Админ Панель*\n\n"
        f"📊 Всего пользователей: {stats.get('total_users', 0)}\n"
        f"📅 Активных записей: {stats.get('active_appointments', 0)}\n"
        f"📰 Новостей: {stats.get('total_news', 0)}\n\n"
        f"Выбери раздел:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_statistics(message: types.Message, bot: Bot):
    """Показать статистику"""
    stats = db.get_stats()
    
    text = (
        f"📊 *Статистика*\n\n"
        f"👥 Всего пользователей: {stats.get('total_users', 0)}\n"
        f"✅ Активных сегодня: {stats.get('active_today', 0)}\n"
        f"📅 Всего записей: {stats.get('total_appointments', 0)}\n"
        f"⏰ Доступных слотов: {stats.get('available_slots', 0)}\n"
        f"📰 Новостей: {stats.get('total_news', 0)}\n"
    )
    
    await message.answer(text, parse_mode="Markdown")


async def show_users(message: types.Message, bot: Bot):
    """Показать список пользователей"""
    users = db.get_all_users(limit=20)
    
    if not users:
        await message.answer("Пользователей пока нет")
        return
    
    text = "👥 *Пользователи:*\n\n"
    
    for user in users:
        username = user.get('username', 'Без username')
        name = user.get('name', 'Без имени')
        rating = user.get('rating', 0)
        text += f"👤 {name} (@{username})\n⭐ Рейтинг: {rating}\n\n"
    
    await message.answer(text, parse_mode="Markdown")


async def show_appointments(message: types.Message, bot: Bot):
    """Показать записи"""
    appointments = db.get_all_appointments(limit=20)
    
    if not appointments:
        await message.answer("Записей пока нет")
        return
    
    text = "📅 *Записи:*\n\n"
    
    for apt in appointments:
        status = apt.get('status', 'pending')
        text += f"📅 {apt.get('date')} в {apt.get('time')}\n"
        text += f"Статус: {status}\n\n"
    
    await message.answer(text, parse_mode="Markdown")


async def show_slots(message: types.Message, bot: Bot):
    """Показать слоты"""
    slots = db.get_all_slots(limit=20)
    
    if not slots:
        await message.answer("Слотов пока нет")
        return
    
    text = "⏰ *Слоты:*\n\n"
    
    for slot in slots:
        status = "Занят" if slot.get('is_booked') else "Свободен"
        text += f"📅 {slot.get('date')} в {slot.get('time')} - {status}\n"
    
    await message.answer(text, parse_mode="Markdown")


async def show_news_panel(message: types.Message, bot: Bot):
    """Показать панель управления новостями"""
    news = db.get_all_news(limit=10)
    
    keyboard = [
        [InlineKeyboardButton(text="➕ Создать новость", callback_data="admin_create_news")],
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    text = "📰 *Управление новостями*\n\n"
    
    if news:
        for n in news:
            text += f"📰 {n.get('title', 'Без названия')}\n"
            text += f"📅 {n.get('created_at', '')}\n\n"
    else:
        text += "Новостей пока нет"
    
    await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")

