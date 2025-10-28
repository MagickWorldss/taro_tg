# 📖 Инструкция: Как заменить эмодзи на реальные изображения

## 🎯 Текущая ситуация

Сейчас бот использует **эмодзи** для визуализации карт таро:
- 🟢 🔥 для Жезлов
- 🟢 💧 для Кубков  
- 🟢 ⚔️ для Мечей
- 🟢 💰 для Пентаклей
- 🟢 🃏 для старших арканов

**Плюсы:**
- ✅ Всегда работает
- ✅ Не требует внешних ресурсов
- ✅ Быстро отображается
- ✅ Работает везде

**Минусы:**
- ❌ Не наглядно как настоящие карты

---

## 🔄 Что нужно сделать для добавления картинок

### Вариант А: Использовать готовый API (самый простой)

**1.** Найти бесплатный API с изображениями таро:
- Labyrinthos (labуrinthos.co)
- Biddy Tarot API
- Tarot API (tarot-api-server.onrender.com)

**2.** Обновить код:
```python
# В tarot_images.py
async def get_tarot_image_url(card_name: str):
    api_url = f"https://tarot-api.onrender.com/api/{card_name}"
    response = await requests.get(api_url)
    return response.json()["image"]
```

**3.** Отправлять фото в Telegram:
```python
# В main.py
image_url = await get_tarot_image_url(card["name"])
await callback.message.answer_photo(
    photo=image_url,
    caption=f"*{card['name']}*\n{interpretation}"
)
```

---

### Вариант Б: Загрузить картинки на GitHub

**1.** Создать папку `images/tarot/` в проекте

**2.** Загрузить изображения (назвать по картам):
```
images/tarot/
├── 0-fool.jpg
├── 1-magician.jpg
├── 2-high-priestess.jpg
...
```

**3.** Использовать GitHub CDN:
```python
# В tarot_images.py
def get_card_image_url(card_name: str) -> str:
    base_url = "https://raw.githubusercontent.com/YOUR_USERNAME/taro_tg/main"
    filename = f"{convert_to_filename(card_name)}.jpg"
    return f"{base_url}/images/tarot/{filename}"
```

**4.** Добавить в `.gitignore` НЕ нужно - файлы должны быть в репозитории

---

### Вариант В: Использовать внешний хостинг

**1.** Загрузить на Imgur (imgur.com) или Cloudinary (cloudinary.com)

**2.** Добавить URL в код:
```python
TAROT_IMAGE_URLS = {
    "Дурак": "https://i.imgur.com/abc123.jpg",
    "Маг": "https://i.imgur.com/def456.jpg",
    # ... и так далее
}
```

---

## 💡 Мое решение для вас

**Рекомендую использовать текущие эмодзи** потому что:

1. ✅ Работает сразу без настройки
2. ✅ Не зависит от внешних сервисов
3. ✅ Бот работает даже если интернет медленный
4. ✅ Эмодзи выглядит нормально в Telegram

**ЕСЛИ всё же нужны картинки:**

Сделайте вот что:
1. Найдите изображения 78 карт (классическая колода Райдер-Уэйт)
2. Загрузите на GitHub в папку `images/`
3. Скажите мне - я обновлю код

**Или:**

Используйте бесплатный API:
```bash
# Пример запроса к Tarot API
curl https://tarot-api-server.onrender.com/api/cards/fool
# Вернет JSON с изображением
```

---

## 📝 Полная инструкция

Смотрите файл `HOW_TO_ADD_IMAGES.md` для детальной инструкции по каждому варианту.

---

## ❓ Вопросы?

Если хотите, чтобы я добавил реальные изображения - напишите! Я найду легальный источник и обновлю код.

