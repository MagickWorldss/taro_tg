"""
Телеграм бот "Твой Таролог"
Основной файл бота
"""
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from handlers import register_all_handlers
from middleware import setup_middleware

# Поддержка PostgreSQL и SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Используем PostgreSQL (Railway)
    from database_postgres_v2 import Database
else:
    # Используем SQLite (fallback)
    from database import Database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Инициализируем БД ПОСЛЕ импорта модулей
db = None  # Будет инициализирован позже

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация базы данных
if DATABASE_URL:
    db = Database()  # PostgreSQL
else:
    db = Database()  # SQLite

class TarotStates(StatesGroup):
    """Состояния для FSM"""
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_birth_place = State()
    waiting_for_photo = State()
    waiting_for_appointment_date = State()
    waiting_for_payment = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "Пользователь"
    
    # Проверяем, существует ли пользователь (асинхронно)
    if DATABASE_URL:
        # PostgreSQL - используем async методы
        if not await db.user_exists(user_id):
            await db.add_user(user_id, username)
        await db.update_last_activity(user_id)
    else:
        # SQLite - используем синхронные методы
        if not db.user_exists(user_id):
            db.add_user(user_id, username)
        db.update_last_activity(user_id)
    
    # Показываем главное меню
    await show_main_menu(message)


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Обработчик команды /menu"""
    await show_main_menu(message)


@dp.callback_query(lambda c: c.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery):
    """Обработка кнопки 'Назад в меню'"""
    await callback.answer()
    await show_main_menu(callback)


async def show_main_menu(message_or_callback):
    """Показывает главное меню"""
    keyboard = [
        [InlineKeyboardButton(text="🌙 Карта дня", callback_data="daily_card")],
        [InlineKeyboardButton(text="🔮 Общий расклад", callback_data="general_reading")],
        [InlineKeyboardButton(text="📅 Запись на личный прием", callback_data="appointment_offline")],
        [InlineKeyboardButton(text="💻 Личный прием онлайн", callback_data="appointment_online")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus")],
        [InlineKeyboardButton(text="📰 Новостная лента", callback_data="news_feed")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    text = "🔮 *Твой Таролог*\n\nВыбери интересующий раздел:"
    
    # Проверяем тип - callback или message
    if isinstance(message_or_callback, CallbackQuery):
        # Callback query - редактируем сообщение
        await message_or_callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # Message - отправляем новое
        await message_or_callback.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


@dp.callback_query(lambda c: c.data == "daily_card")
async def handle_daily_card(callback: CallbackQuery):
    """Обработка карты дня"""
    from tarot_cards import get_daily_card
    from tarot_images import get_card_full_info, get_tarot_image_from_api
    
    await callback.answer()
    
    card, is_reversed = get_daily_card()
    interpretation = get_card_meaning(card, is_reversed)
    
    # Получаем визуализацию карты
    card_visual = get_card_full_info(card, is_reversed)
    status_text = "🔴 ПЕРЕВЕРНУТА" if is_reversed else "🟢 ПРЯМАЯ"
    
    # Пробуем получить изображение
    image_url = await get_tarot_image_from_api(card["name"])
    
    # Добавляем кнопку "Назад"
    keyboard = [
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    text = (
        f"🌙 *Твоя карта дня*\n\n"
        f"*{card['name']}*\n"
        f"Позиция: {status_text}\n\n"
        f"*Толкование:*\n{interpretation}\n\n"
        f"_Следующая карта будет доступна через 24 часа_"
    )
    
    # Если есть изображение - отправляем фото
    if image_url:
        try:
            # Проверяем это локальный файл или URL
            if image_url.startswith("http"):
                # Это URL - отправляем как есть
                await callback.message.answer_photo(
                    photo=image_url,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            else:
                # Это локальный файл - используем FSInputFile
                from aiogram.types import FSInputFile
                photo = FSInputFile(image_url)
                await callback.message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            return
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
    
    # Fallback - текст с эмодзи
    await callback.message.edit_text(
        f"🌙 *Твоя карта дня*\n\n{card_visual}*Толкование:*\n{interpretation}\n\n_Следующая карта будет доступна через 24 часа_",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "general_reading")
async def handle_general_reading(callback: CallbackQuery):
    """Обработка общего расклада на 3 карты"""
    from tarot_cards import get_three_card_reading
    from tarot_images import get_card_image_url
    
    await callback.answer()
    
    cards = get_three_card_reading()
    interpretation = get_combined_reading(cards)
    
    positions = ["Прошлое", "Настоящее", "Будущее"]
    cards_text = ""
    
    for i, (card, is_reversed) in enumerate(cards, 1):
        position = positions[i-1] if i <= len(positions) else f"Позиция {i}"
        status = "перевернута" if is_reversed else "прямая"
        emoji = get_card_image_url(card['name'], is_reversed)
        cards_text += f"{emoji} {i}. *{card['name']}* ({status})\n📍 {position}\n\n"
    
    keyboard = [[InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        f"🔮 *Общий расклад на 3 карты*\n\n"
        f"{cards_text}\n"
        f"*Комбинированное толкование:*\n\n{interpretation}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "profile")
async def handle_profile(callback: CallbackQuery):
    """Обработка профиля"""
    await callback.answer()
    
    # Получаем пользователя
    if DATABASE_URL:
        user = await db.get_user(callback.from_user.id)
    else:
        user = db.get_user(callback.from_user.id)
    
    if user:
        text = (
            f"👤 *Твой профиль*\n\n"
            f"ID: `{callback.from_user.id}`\n"
            f"Username: @{callback.from_user.username or 'Не указан'}\n"
            f"Имя: {user.get('name', 'Не указано')}\n"
            f"Дата рождения: {user.get('birth_date', 'Не указано')}\n"
            f"Время рождения: {user.get('birth_time', 'Не указано')}\n"
            f"Место рождения: {user.get('birth_place', 'Не указано')}\n"
            f"Рейтинг: ⭐ {user.get('rating', 0)}\n"
        )
    else:
        text = "Профиль не найден. Данные еще не заполнены."
    
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


@dp.callback_query(lambda c: c.data == "bonus")
async def handle_bonus(callback: CallbackQuery):
    """Обработка раздела Бонус"""
    await callback.answer()
    
    keyboard = [[InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "🎁 *Бонус раздел*\n\n"
        "Скоро здесь будет открыт специальный раздел с уникальными возможностями! ✨\n\n"
        "Следи за обновлениями в новостной ленте 🔮",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "news_feed")
async def handle_news_feed(callback: CallbackQuery):
    """Обработка новостной ленты"""
    from lunar_calendar import get_lunar_info
    
    await callback.answer()
    
    lunar_info = get_lunar_info()
    
    keyboard = [[InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        f"📰 *Новостная лента*\n\n"
        f"🌙 {lunar_info['day']}\n"
        f"📅 Фаза луны: {lunar_info['phase']}\n"
        f"🌍 Знак луны: {lunar_info['sign']}\n\n"
        f"{lunar_info['recommendation']}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "appointment_online")
async def handle_online_appointment(callback: CallbackQuery):
    """Обработка личного приема онлайн - открывает чат с админом"""
    await callback.answer()
    
    admin_id = os.getenv("ADMIN_ID")
    keyboard = [
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    if admin_id:
        await callback.message.edit_text(
            "💻 *Личный прием онлайн*\n\n"
            "Для записи на онлайн консультацию напишите напрямую:\n"
            f"👤 @{os.getenv('ADMIN_USERNAME', 'admin')}\n\n"
            "Или нажмите кнопку ниже для быстрого перехода:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "💻 *Личный прием онлайн*\n\n"
            "Для записи на онлайн консультацию напишите напрямую администратору.\n\n"
            "Мы свяжемся с вами в ближайшее время.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


@dp.callback_query(lambda c: c.data == "appointment_offline")
async def handle_offline_appointment(callback: CallbackQuery):
    """Обработка записи на личный прием"""
    await callback.answer()
    
    # Получаем доступные слоты
    if DATABASE_URL:
        slots = await db.get_available_slots()
    else:
        slots = db.get_available_slots()
    
    if not slots:
        keyboard = [[InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await callback.message.edit_text(
            "📅 *Запись на личный прием*\n\n"
            "К сожалению, в данный момент нет доступных слотов для записи.\n"
            "Попробуйте позже или свяжитесь с администратором.\n\n"
            "Для быстрой связи напишите:\n@администратор",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return
    
    # Создаем клавиатуру с доступными слотами
    keyboard = []
    for slot in slots[:10]:  # Показываем первые 10 слотов
        date_str = slot['date']
        time_str = slot['time']
        slot_id = slot['id']
        keyboard.append([InlineKeyboardButton(
            text=f"📅 {date_str} в {time_str}",
            callback_data=f"slot_{slot_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "📅 *Запись на личный прием*\n\n"
        "Консультация длится 1 час.\n"
        "Выбери удобное время:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


def get_card_meaning(card, is_reversed):
    """Получить развернутое толкование карты"""
    if is_reversed:
        return f"{card.get('reversed', 'Значение перевернутой карты не определено')}"
    else:
        return f"{card.get('upright', 'Значение карты не определено')}"


def get_combined_reading(cards):
    """Получить комбинированное толкование для 3 карт"""
    # Здесь логика комбинации значений карт
    # Для примера возвращаем базовое толкование
    interpretations = []
    positions = ["Прошлое", "Настоящее", "Будущее"]
    
    for i, (card, is_reversed) in enumerate(cards):
        position = positions[i] if i < len(positions) else "Позиция"
        meaning = get_card_meaning(card, is_reversed)
        interpretations.append(f"{position}: {meaning}")
    
    return "\n\n".join(interpretations)


async def main():
    """Запуск бота"""
    logger.info("Запуск бота...")
    
    # Регистрация всех обработчиков
    register_all_handlers(dp)
    
    # Настройка middleware
    setup_middleware(dp)
    
    try:
        # Инициализация БД при первом запуске
        if DATABASE_URL:
            # PostgreSQL - инициализируем структуру
            logger.info("Инициализация PostgreSQL...")
            await db.init_db()
            logger.info("PostgreSQL готов к работе")
        else:
            # SQLite - проверяем и создаем
            import sqlite3
            import os
            
            db_exists = os.path.exists(db.db_path)
            
            if not db_exists:
                db.init_db()
                logger.info("База данных SQLite создана")
            else:
                try:
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                    result = cursor.fetchone()
                    conn.close()
                    
                    if not result:
                        logger.info("База данных найдена, но таблиц нет. Создаем структуру...")
                        db.init_db()
                    else:
                        logger.info("База данных подключена и структура существует")
                except Exception as e:
                    logger.warning(f"Ошибка проверки БД: {e}. Создаем заново...")
                    db.init_db()
        
        # Запуск polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

