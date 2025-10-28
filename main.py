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
        try:
            # Callback query - пытаемся редактировать сообщение
            await message_or_callback.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            # Если не можем редактировать (например, предыдущее сообщение было фото),
            # отправляем новое сообщение
            logger.debug(f"Не могу редактировать сообщение: {e}, отправляю новое")
            await message_or_callback.message.answer(
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
    from tarot_cards import get_daily_card, get_card_meaning
    from tarot_images import get_card_full_info, get_tarot_image_from_api
    from datetime import datetime, timedelta
    
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Проверяем, можно ли получить карту дня
    if DATABASE_URL:
        can_get = await db.can_get_daily_card(user_id)
        
        if not can_get:
            # Пытаемся получить сохраненную карту
            saved_card_data = await db.get_daily_card_data(user_id)
            
            if saved_card_data:
                card = saved_card_data
                is_reversed = saved_card_data.get('is_reversed', False)
                interpretation = get_card_meaning(card, is_reversed)
            else:
                # Не можем получить карту и нет сохраненной - показываем ошибку
                keyboard = [[InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]]
                reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                await callback.message.edit_text(
                    "⏰ Ты уже получил карту дня! Следующая карта будет доступна через 24 часа.",
                    reply_markup=reply_markup
                )
                return
            
            # Получаем тайминг следующей карты
            try:
                row = await db.get_user(user_id)
                if row and row.get('last_daily_card'):
                    last_time = row['last_daily_card']
                    if isinstance(last_time, str):
                        last_time = datetime.fromisoformat(last_time)
                    next_time = last_time + timedelta(hours=24)
                    hours_left = (next_time - datetime.now()).total_seconds() / 3600
                    hours_left = max(0, int(hours_left))
                else:
                    hours_left = 24
            except:
                hours_left = 24
        else:
            # Можно получить новую карту
            card, is_reversed = get_daily_card(user_id=user_id)
            interpretation = get_card_meaning(card, is_reversed)
            
            # Сохраняем данные карты
            await db.save_daily_card(user_id, {
                'name': card['name'],
                'upright': card.get('upright', ''),
                'reversed': card.get('reversed', ''),
                'is_reversed': is_reversed
            })
            
            hours_left = 24
    else:
        # Для SQLite без проверки времени
        card, is_reversed = get_daily_card(user_id=user_id)
        interpretation = get_card_meaning(card, is_reversed)
        hours_left = 24
    
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
    
    # Формируем сообщение о времени до следующей карты
    if hours_left == 24:
        time_text = "_Следующая карта будет доступна завтра_"
    elif hours_left > 0:
        time_text = f"_Следующая карта будет доступна через {hours_left} час(ов)_"
    else:
        time_text = "_Следующая карта доступна!_"
    
    text = (
        f"🌙 *Твоя карта дня*\n\n"
        f"*{card['name']}*\n"
        f"Позиция: {status_text}\n\n"
        f"*Толкование:*\n{interpretation}\n\n"
        f"{time_text}"
    )
    
    # Если есть изображение - отправляем фото
    if image_url:
        try:
            from aiogram.types import BufferedInputFile
            import aiohttp
            from PIL import Image
            import io
            
            # Загружаем изображение
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        
                        # Если карта перевернута - поворачиваем изображение
                        if is_reversed:
                            # Открываем изображение
                            img = Image.open(io.BytesIO(image_bytes))
                            # Поворачиваем на 180 градусов
                            img_rotated = img.rotate(180)
                            
                            # Сохраняем в байты
                            output = io.BytesIO()
                            img_rotated.save(output, format='JPEG')
                            image_bytes = output.getvalue()
                        
                        # Отправляем фото
                        photo = BufferedInputFile(
                            file=image_bytes,
                            filename=f"{card['name']}.jpg"
                        )
                        
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
    from tarot_cards import get_three_card_reading, get_card_meaning
    from tarot_images import get_tarot_image_from_api
    
    await callback.answer()
    
    cards = get_three_card_reading()
    interpretation = get_combined_reading(cards)
    
    positions = ["Прошлое", "Настоящее", "Будущее"]
    
    # Собираем изображения для медиа-группы
    from aiogram.types import InputMediaPhoto, BufferedInputFile
    import aiohttp
    from PIL import Image
    import io
    
    media_group = []
    
    try:
        async with aiohttp.ClientSession() as session:
            for i, (card, is_reversed) in enumerate(cards):
                position = positions[i] if i < len(positions) else f"Позиция {i+1}"
                status = "🔴 ПЕРЕВЕРНУТА" if is_reversed else "🟢 ПРЯМАЯ"
                
                # Получаем URL изображения
                image_url = await get_tarot_image_from_api(card["name"])
                
                if image_url:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_bytes = await response.read()
                            
                            # Если карта перевернута - поворачиваем
                            if is_reversed:
                                img = Image.open(io.BytesIO(image_bytes))
                                img_rotated = img.rotate(180)
                                output = io.BytesIO()
                                img_rotated.save(output, format='JPEG')
                                image_bytes = output.getvalue()
                            
                            # Формируем caption для карты
                            caption = f"*{card['name']}*\n{status}\n📍 {position}"
                            
                            # Создаем фото для медиа-группы
                            photo = BufferedInputFile(
                                file=image_bytes,
                                filename=f"{card['name']}.jpg"
                            )
                            
                            media_group.append(
                                InputMediaPhoto(
                                    media=photo,
                                    caption=caption,
                                    parse_mode="Markdown"
                                )
                            )
        # Отправляем медиа-группу
        if media_group:
            # Последнее фото без caption (чтобы добавить толкование отдельным сообщением)
            # Удаляем caption с последнего, чтобы добавить его отдельным сообщением
            caption_text = (
                f"🔮 *Общий расклад на 3 карты*\n\n"
                f"*Комбинированное толкование:*\n\n{interpretation}"
            )
            
            keyboard = [[InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            # Отправляем медиа-группу
            await callback.message.answer_media_group(media=media_group)
            
            # Отправляем толкование отдельным сообщением с кнопкой
            await callback.message.answer(
                caption_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return
    except Exception as e:
        logger.error(f"Ошибка отправки расклада: {e}")
    
    # Fallback - отправляем текстом если что-то пошло не так
    cards_text = ""
    for i, (card, is_reversed) in enumerate(cards, 1):
        position = positions[i-1] if i <= len(positions) else f"Позиция {i}"
        status = "перевернута" if is_reversed else "прямая"
        cards_text += f"{i}. *{card['name']}* ({status})\n📍 {position}\n\n"
    
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
    
    # Формируем текст без Markdown для избежания ошибок
    if user:
        name = user.get('name', 'Не указано') or 'Не указано'
        birth_date = user.get('birth_date', 'Не указано') or 'Не указано'
        birth_time = user.get('birth_time', 'Не указано') or 'Не указано'
        birth_place = user.get('birth_place', 'Не указано') or 'Не указано'
        rating = user.get('rating', 0) or 0
        
        text = (
            f"👤 Твой профиль\n\n"
            f"ID: {callback.from_user.id}\n"
            f"Username: @{callback.from_user.username or 'Не указан'}\n"
            f"Имя: {name}\n"
            f"Дата рождения: {birth_date}\n"
            f"Время рождения: {birth_time}\n"
            f"Место рождения: {birth_place}\n"
            f"Рейтинг: ⭐ {rating}\n"
        )
    else:
        text = "Профиль не найден. Данные еще не заполнены."
    
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(text, reply_markup=reply_markup)


@dp.callback_query(lambda c: c.data == "edit_profile")
async def handle_edit_profile(callback: CallbackQuery):
    """Обработка редактирования профиля"""
    await callback.answer()
    
    keyboard = [
        [InlineKeyboardButton(text="📝 Имя", callback_data="edit_name")],
        [InlineKeyboardButton(text="📅 Дата рождения", callback_data="edit_birth_date")],
        [InlineKeyboardButton(text="🕐 Время рождения", callback_data="edit_birth_time")],
        [InlineKeyboardButton(text="📍 Место рождения", callback_data="edit_birth_place")],
        [InlineKeyboardButton(text="◀️ Назад к профилю", callback_data="profile")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "✏️ *Редактирование профиля*\n\n"
        "Выбери, что хочешь изменить:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "edit_name")
async def handle_edit_name(callback: CallbackQuery, state: FSMContext):
    """Обработка редактирования имени"""
    await callback.answer()
    await state.set_state(TarotStates.waiting_for_name)
    
    keyboard = [[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "📝 *Введи свое имя*\n\n"
        "Отправь новое имя или нажми Отмена:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "edit_birth_date")
async def handle_edit_birth_date(callback: CallbackQuery, state: FSMContext):
    """Обработка редактирования даты рождения"""
    await callback.answer()
    await state.set_state(TarotStates.waiting_for_birth_date)
    
    keyboard = [[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "📅 *Введи дату рождения*\n\n"
        "Формат: ДД.ММ.ГГГГ (например, 15.03.1990)\n"
        "Или нажми Отмена:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "edit_birth_time")
async def handle_edit_birth_time(callback: CallbackQuery, state: FSMContext):
    """Обработка редактирования времени рождения"""
    await callback.answer()
    await state.set_state(TarotStates.waiting_for_birth_time)
    
    keyboard = [[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "🕐 *Введи время рождения*\n\n"
        "Формат: ЧЧ:ММ (например, 14:30)\n"
        "Или нажми Отмена:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "edit_birth_place")
async def handle_edit_birth_place(callback: CallbackQuery, state: FSMContext):
    """Обработка редактирования места рождения"""
    await callback.answer()
    await state.set_state(TarotStates.waiting_for_birth_place)
    
    keyboard = [[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "📍 *Введи место рождения*\n\n"
        "Например: Москва, Россия\n"
        "Или нажми Отмена:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "cancel_edit")
async def handle_cancel_edit(callback: CallbackQuery, state: FSMContext):
    """Обработка отмены редактирования"""
    await callback.answer()
    await state.clear()
    
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "❌ Редактирование отменено",
        reply_markup=reply_markup
    )


# Обработчики для получения текста от пользователя
@dp.message(TarotStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обработка введенного имени"""
    name = message.text
    
    # Сохраняем в БД
    if DATABASE_URL:
        await db.update_user(message.from_user.id, name=name)
    else:
        db.update_user(message.from_user.id, name=name)
    
    await state.clear()
    
    keyboard = [
        [InlineKeyboardButton(text="◀️ К профилю", callback_data="profile")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        f"✅ Имя обновлено: {name}",
        reply_markup=reply_markup
    )


@dp.message(TarotStates.waiting_for_birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    """Обработка введенной даты рождения"""
    birth_date = message.text
    
    # Сохраняем в БД
    if DATABASE_URL:
        await db.update_user(message.from_user.id, birth_date=birth_date)
    else:
        db.update_user(message.from_user.id, birth_date=birth_date)
    
    await state.clear()
    
    keyboard = [[InlineKeyboardButton(text="◀️ К профилю", callback_data="profile")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        f"✅ Дата рождения обновлена: {birth_date}",
        reply_markup=reply_markup
    )


@dp.message(TarotStates.waiting_for_birth_time)
async def process_birth_time(message: types.Message, state: FSMContext):
    """Обработка введенного времени рождения"""
    birth_time = message.text
    
    # Сохраняем в БД
    if DATABASE_URL:
        await db.update_user(message.from_user.id, birth_time=birth_time)
    else:
        db.update_user(message.from_user.id, birth_time=birth_time)
    
    await state.clear()
    
    keyboard = [[InlineKeyboardButton(text="◀️ К профилю", callback_data="profile")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        f"✅ Время рождения обновлено: {birth_time}",
        reply_markup=reply_markup
    )


@dp.message(TarotStates.waiting_for_birth_place)
async def process_birth_place(message: types.Message, state: FSMContext):
    """Обработка введенного места рождения"""
    birth_place = message.text
    
    # Сохраняем в БД
    if DATABASE_URL:
        await db.update_user(message.from_user.id, birth_place=birth_place)
    else:
        db.update_user(message.from_user.id, birth_place=birth_place)
    
    await state.clear()
    
    keyboard = [[InlineKeyboardButton(text="◀️ К профилю", callback_data="profile")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        f"✅ Место рождения обновлено: {birth_place}",
        reply_markup=reply_markup
    )


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

