"""
Скрипт для создания тестовых слотов в базе данных
"""
from database import Database
from datetime import datetime, timedelta

def create_test_slots():
    """Создать тестовые слоты на ближайшие 7 дней"""
    db = Database()
    import sqlite3
    
    # Создаем БД если ее нет
    db.init_db()
    
    conn = sqlite3.connect(db.db_path)
    
    # Определяем даты на 7 дней вперед
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    # Временные слоты (10:00 - 19:00 каждый час)
    times = [f"{hour:02d}:00" for hour in range(10, 20)]
    
    slots_added = 0
    
    for date in dates:
        for time in times:
            # Проверяем, существует ли уже такой слот
            cursor = conn.execute(
                "SELECT COUNT(*) FROM slots WHERE date = ? AND time = ?",
                (date, time)
            )
            exists = cursor.fetchone()[0]
            
            if not exists:
                conn.execute(
                    "INSERT INTO slots (date, time, is_booked) VALUES (?, ?, 0)",
                    (date, time)
                )
                slots_added += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Создано {slots_added} новых слотов")
    print(f"📅 На {len(dates)} дней вперед")
    print(f"⏰ {len(times)} временных слотов в день")
    print(f"📊 Всего слотов: {slots_added}")


if __name__ == "__main__":
    print("🚀 Создание тестовых слотов для календаря...")
    create_test_slots()
    print("✅ Готово!")

