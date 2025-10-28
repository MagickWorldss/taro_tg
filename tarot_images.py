"""
Модуль для отображения изображений карт таро
Использует бесплатные изображения из открытых источников
"""
from typing import Optional, Dict
import aiohttp
import logging

logger = logging.getLogger(__name__)


# База изображений карт таро (общественное достояние)
# Используем эмодзи как fallback, но можно заменить на реальные изображения

# Бесплатный API для изображений таро
# tarot-api-server.onrender.com или альтернативные источники
TAROT_API_BASE = "https://tarot-api-server.onrender.com/api/cards"

# Fallback API если основной не работает
FALLBACK_API = "https://api.lostmy.name/tarot"

# Mapping русских названий к английским (для API)
CARD_NAME_MAPPING = {
    "Дурак": "fool",
    "Маг": "magician",
    "Жрица": "high-priestess",
    "Императрица": "empress",
    "Император": "emperor",
    "Иерофант": "hierophant",
    "Влюбленные": "lovers",
    "Колесница": "chariot",
    "Сила": "strength",
    "Отшельник": "hermit",
    "Колесо Фортуны": "wheel-of-fortune",
    "Справедливость": "justice",
    "Повешенный": "hanged-man",
    "Смерть": "death",
    "Умеренность": "temperance",
    "Дьявол": "devil",
    "Башня": "tower",
    "Звезда": "star",
    "Луна": "moon",
    "Солнце": "sun",
    "Суд": "judgement",
    "Мир": "world",
}


async def get_tarot_image_from_api(card_name: str) -> Optional[str]:
    """
    Получить путь к изображению карты из локальных файлов
    """
    try:
        from card_image_mapping import get_card_image_path, CARD_TO_IMAGE_PATH
        
        # Проверяем локальные файлы
        image_path = get_card_image_path(card_name)
        
        if image_path and os.path.exists(image_path):
            logger.info(f"Локальное изображение найдено: {card_name}")
            return image_path
        
        # Проверяем есть ли в словаре (если загружены на GitHub)
        if card_name in TAROT_IMAGE_URLS and TAROT_IMAGE_URLS[card_name]:
            return TAROT_IMAGE_URLS[card_name]
        
        return None
    except Exception as e:
        logger.debug(f"Изображение не найдено для {card_name}: {e}")
        return None


# Словарь с прямыми ссылками на изображения карт таро
# Добавьте сюда ссылки на ваши изображения
# Пример: "Дурак": "https://imgur.com/abc123.jpg"
TAROT_IMAGE_URLS = {
    # ВОТ СЮДА ДОБАВЬТЕ ВАШИ ИЗОБРАЖЕНИЯ!
    # Например:
    # "Дурак": "https://imgur.com/fool.jpg",
    # "Маг": "https://imgur.com/magician.jpg",
    # ...
}


def get_card_image_url(card_name: str, is_reversed: bool = False) -> str:
    """
    Получить изображение карты
    
    Возвращает эмодзи как визуализацию
    В будущем можно заменить на реальные URL изображений
    """
    image_emojis = {
        # Старшие арканы
        "Дурак": "🃏",
        "Маг": "🪄",
        "Жрица": "🔮",
        "Императрица": "👑",
        "Император": "⚔️",
        "Иерофант": "📿",
        "Влюбленные": "💕",
        "Колесница": "🏁",
        "Сила": "💪",
        "Отшельник": "🕯️",
        "Колесо Фортуны": "♻️",
        "Справедливость": "⚖️",
        "Повешенный": "⏳",
        "Смерть": "💀",
        "Умеренность": "🧘",
        "Дьявол": "😈",
        "Башня": "🗼",
        "Звезда": "⭐",
        "Луна": "🌙",
        "Солнце": "☀️",
        "Суд": "👁️",
        "Мир": "🌍",
    }
    
    # Эмодзи для мастей
    suit_emojis = {
        "Жезлов": "🔥",
        "Кубков": "💧",
        "Мечей": "⚔️",
        "Пентаклей": "💰"
    }
    
    # Определяем эмодзи для карты
    emoji = image_emojis.get(card_name, "🃏")
    
    # Если это масть, добавляем эмодзи масти
    for suit, suit_emoji in suit_emojis.items():
        if suit in card_name:
            emoji = suit_emoji
            break
    
    # Для перевернутой карты добавляем индикатор
    if is_reversed:
        emoji = f"🔴 {emoji}"
    else:
        emoji = f"🟢 {emoji}"
    
    return emoji


def get_card_full_info(card: Dict, is_reversed: bool) -> str:
    """
    Получить полную информацию о карте с визуализацией
    """
    card_name = card["name"]
    emoji = get_card_image_url(card_name, is_reversed)
    
    status = "ПЕРЕВЕРНУТА" if is_reversed else "ПРЯМАЯ"
    
    info = f"""
{emoji} *{card_name}*
Позиция: {status}

"""
    
    return info


# Для добавления реальных изображений:
# 1. Загрузите изображения в папку images/tarot/
# 2. Добавьте URL в словарь TAROT_IMAGE_URLS
# 3. Обновите функцию get_card_image_url для возврата URL
#
# Пример:
# def get_card_image_url(card_name: str, is_reversed: bool = False) -> Optional[str]:
#     if card_name in TAROT_IMAGE_URLS:
#         return TAROT_IMAGE_URLS[card_name]
#     return None  # Будет использован эмодзи

def send_card_with_image(bot, chat_id: int, card: Dict, is_reversed: bool, text: str):
    """
    Отправить карту с изображением
    
    Если есть URL изображения - отправляет фото
    Если нет - отправляет текст с эмодзи
    """
    card_name = card["name"]
    
    # Проверяем, есть ли URL изображения
    if card_name in TAROT_IMAGE_URLS:
        image_url = TAROT_IMAGE_URLS[card_name]
        # TODO: Реализовать отправку фото через bot.send_photo()
        # await bot.send_photo(chat_id=chat_id, photo=image_url, caption=text)
        return text  # Временная реализация
    else:
        return text

