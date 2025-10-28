# 🖼️ Как добавить изображения карт таро

## ⚠️ Важное замечание

Railway **не хранит файлы после деплоя**. Используйте внешние источники изображений.

## 🎯 Три способа добавить изображения

### Вариант 1: Использовать бесплатный API (рекомендуется)

Используйте бесплатный API с изображениями таро карт:

```python
# Добавьте в tarot_images.py

TAROT_IMAGE_API = "https://tarot-api-server.onrender.com/api/cards"

def get_card_image_url(card_name: str) -> str:
    """Получить URL изображения из API"""
    # Конвертируем название карты в API формат
    api_name = convert_card_name_to_api_format(card_name)
    return f"{TAROT_IMAGE_API}/{api_name}"
```

### Вариант 2: GitHub CDN (raw.githubusercontent.com)

1. Создайте папку `images/` в вашем репозитории
2. Загрузите изображения карт
3. Используйте GitHub CDN URL:

```python
# Пример для card_0_fool.png
image_url = f"https://raw.githubusercontent.com/YOUR_USERNAME/taro_tg/main/images/card_0_fool.png"
```

### Вариант 3: Внешний хостинг изображений

1. **Imgur** (бесплатно):
   - Загрузите изображения на imgur.com
   - Получите прямые ссылки

2. **Cloudinary** (бесплатно до 25GB):
   - Создайте аккаунт cloudinary.com
   - Загрузите изображения
   - Получите URL

---

## 📝 Инструкция по внедрению

### Шаг 1: Найти изображения карт

Бесплатные источники:
- [Labyrinthos Academy](https://labyrinthos.co/blogs/tarot-card-meanings-list)
- [Biddy Tarot](https://www.biddytarot.com/tarot-card-meanings/)
- [Проект Tarot API](https://github.com/ekelen/tarot-api)

### Шаг 2: Обновить tarot_images.py

```python
# Полный список URL для всех 78 карт
TAROT_IMAGE_URLS = {
    # Старшие арканы
    "Дурак": "https://example.com/images/0-fool.jpg",
    "Маг": "https://example.com/images/1-magician.jpg",
    "Жрица": "https://example.com/images/2-high-priestess.jpg",
    # ... и так далее для всех 78 карт
}
```

### Шаг 3: Обновить отправку карт в main.py

```python
from aiogram.types import FSInputFile

@dp.callback_query(lambda c: c.data == "daily_card")
async def handle_daily_card(callback: CallbackQuery):
    """Обработка карты дня с изображением"""
    from tarot_cards import get_daily_card
    from tarot_images import get_card_image_url
    
    card, is_reversed = get_daily_card()
    interpretation = get_card_meaning(card, is_reversed)
    
    # Получаем URL изображения
    image_url = get_card_image_url(card["name"], is_reversed)
    
    # Отправляем фото вместо текста
    if image_url:
        await callback.message.answer_photo(
            photo=image_url,
            caption=f"🌙 *Твоя карта дня*\n\n"
                   f"*{card['name']}*\n"
                   f"Позиция: {'ПЕРЕВЕРНУТА' if is_reversed else 'ПРЯМАЯ'}\n\n"
                   f"*Толкование:*\n{interpretation}",
            parse_mode="Markdown"
        )
    else:
        # Fallback на текст с эмодзи
        await callback.message.edit_text(...)
    
    await callback.answer()
```

---

## 🚀 Быстрое решение: Используйте готовый API

Есть бесплатные API которые уже предоставляют изображения таро:

### 1. Tarot API

```python
import requests

def get_tarot_card_image(card_name: str) -> str:
    """Получить изображение из Tarot API"""
    api = f"https://tarot-api-server.onrender.com/api/cards"
    response = requests.get(api)
    cards = response.json()
    
    for card in cards:
        if card["name"].lower() == card_name.lower():
            return card["image"]
    
    return None
```

### 2. Labyrinthos API

```python
def get_labyrinthos_image(card_name: str) -> str:
    """Labyrinthos предоставляет изображения"""
    # Конвертируем название в slug
    slug = card_name.lower().replace(" ", "-")
    return f"https://labyrinthos.co/static/{slug}.jpg"
```

---

## 📦 Альтернатива: Хранить в коде

Если API недоступны, можно использовать base64 encoded images:

```python
import base64

TAROT_IMAGES_BASE64 = {
    "Дурак": "data:image/png;base64,iVBORw0KGgo...",  # Base64 encoded image
    # ...
}

def get_card_image_base64(card_name: str) -> str:
    return TAROT_IMAGES_BASE64.get(card_name, "")
```

---

## ⚡ Рекомендуемое решение

**Используйте комплексный подход:**

1. **API как основной источник** (fast, no storage)
2. **Эмодзи как fallback** (всегда работает)
3. **Ленивая загрузка** (только при запросе)

```python
async def send_card(bot, chat_id, card_name, is_reversed):
    """Умная отправка карты с fallback"""
    try:
        # Пробуем API
        image_url = await get_tarot_api_image(card_name)
        await bot.send_photo(chat_id=chat_id, photo=image_url, caption=text)
    except:
        # Fallback на эмодзи
        emoji = get_card_emoji(card_name, is_reversed)
        await bot.send_message(chat_id=chat_id, text=f"{emoji} {card_name}\n{text}")
```

---

## ✅ Практический план действий

1. **Выберите источник** (API или хостинг)
2. **Обновите `tarot_images.py`** с URL карт
3. **Добавьте логику отправки фото** в `main.py`
4. **Протестируйте** локально
5. **Задеплойте** на Railway

---

## 📞 Нужна помощь?

Если нужна конкретная реализация - дайте знать и я подготовлю код!

