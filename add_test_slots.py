"""
Скрипт для добавления тестовых слотов в базу данных
Запустить после деплоя на Railway
"""
import asyncio
import os
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

async def add_slots():
    """Добавить тестовые слоты"""
    if not DATABASE_URL:
        print("DATABASE_URL не установлен")
        return
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Добавляем тестовые слоты на ближайшие дни
    from datetime import datetime, timedelta
    
    slots = []
    for day in range(7):  # 7 дней
        date = datetime.now() + timedelta(days=day+1)
        date_str = date.strftime("%d.%m.%Y")
        
        # Добавляем 3 слота в день: 10:00, 14:00, 18:00
        for hour in [10, 14, 18]:
            time_str = f"{hour}:00"
            
            # Проверяем, существует ли уже такой слот
            existing = await conn.fetchrow(
                "SELECT id FROM slots WHERE date = $1 AND time = $2",
                date_str, time_str
            )
            
            if not existing:
                slots.append((date_str, time_str))
    
    # Вставляем слоты
    for date_str, time_str in slots:
        await conn.execute(
            "INSERT INTO slots (date, time, is_booked) VALUES ($1, $2, FALSE)",
            date_str, time_str
        )
        print(f"✅ Добавлен слот: {date_str} в {time_str}")
    
    await conn.close()
    print(f"\n✅ Всего добавлено слотов: {len(slots)}")

if __name__ == "__main__":
    asyncio.run(add_slots())

