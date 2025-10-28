"""
Модуль для работы с PostgreSQL базой данных
Асинхронная версия для Railway
"""
import asyncpg
import logging
import os
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с PostgreSQL базой данных"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
        if not self.database_url:
            logger.warning("DATABASE_URL не установлен, PostgreSQL недоступен")
    
    async def get_pool(self):
        """Получить пул соединений"""
        if self.pool is None and self.database_url:
            try:
                self.pool = await asyncpg.create_pool(self.database_url)
                logger.info("Подключение к PostgreSQL установлено")
            except Exception as e:
                logger.error(f"Ошибка подключения к PostgreSQL: {e}")
        return self.pool
    
    async def init_db(self):
        """Инициализация базы данных PostgreSQL"""
        pool = await self.get_pool()
        if not pool:
            logger.error("Не удалось подключиться к PostgreSQL")
            return
        
        async with pool.acquire() as conn:
            # Таблица пользователей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    name TEXT,
                    birth_date TEXT,
                    birth_time TEXT,
                    birth_place TEXT,
                    photo TEXT,
                    rating INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'ru',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_daily_card TIMESTAMP,
                    daily_card_data TEXT
                )
            """)
            
            # Проверяем и добавляем новые столбцы если нужно (для существующих таблиц)
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_daily_card TIMESTAMP")
            except Exception as e:
                logger.debug(f"Столбец last_daily_card уже существует: {e}")
            
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_card_data TEXT")
            except Exception as e:
                logger.debug(f"Столбец daily_card_data уже существует: {e}")
            
            logger.info("База данных PostgreSQL инициализирована")
    
    # Методы для пользователей
    async def user_exists(self, user_id: int) -> bool:
        """Проверить существование пользователя"""
        pool = await self.get_pool()
        if not pool:
            return False
        
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT 1 FROM users WHERE user_id = $1",
                    user_id
                )
                return row is not None
        except:
            return False
    
    async def add_user(self, user_id: int, username: str, name: str = None):
        """Добавить пользователя"""
        pool = await self.get_pool()
        if not pool:
            return
        
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO users (user_id, username, name) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO NOTHING",
                    user_id, username, name
                )
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя"""
        pool = await self.get_pool()
        if not pool:
            return None
        
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1",
                    user_id
                )
                if row:
                    return dict(row)
        except:
            pass
        return None
    
    async def update_user(self, user_id: int, **kwargs):
        """Обновить данные пользователя"""
        pool = await self.get_pool()
        if not pool:
            return
        
        if not kwargs:
            return
        
        try:
            set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(kwargs.keys())])
            values = list(kwargs.values()) + [user_id]
            query = f"UPDATE users SET {set_clause} WHERE user_id = $1"
            
            async with pool.acquire() as conn:
                await conn.execute(query, *values)
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя: {e}")
    
    async def update_last_activity(self, user_id: int):
        """Обновить время последней активности"""
        pool = await self.get_pool()
        if not pool:
            return
        
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = $1",
                    user_id
                )
        except:
            pass
    
    # Методы для слотов
    async def get_available_slots(self) -> List[Dict]:
        """Получить доступные слоты"""
        pool = await self.get_pool()
        if not pool:
            return []
        
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM slots WHERE is_booked = FALSE ORDER BY date, time LIMIT 20"
                )
                return [dict(row) for row in rows]
        except:
            return []
    
    async def book_slot(self, user_id: int, slot_id: int, appointment_type: str):
        """Забронировать слот"""
        pool = await self.get_pool()
        if not pool:
            return
        
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        "INSERT INTO appointments (user_id, slot_id, appointment_type) VALUES ($1, $2, $3)",
                        user_id, slot_id, appointment_type
                    )
                    await conn.execute(
                        "UPDATE slots SET is_booked = TRUE WHERE id = $1",
                        slot_id
                    )
        except Exception as e:
            logger.error(f"Ошибка бронирования слота: {e}")
    
    async def can_get_daily_card(self, user_id: int) -> bool:
        """Проверить, можно ли получить карту дня (прошло ли 24 часа)"""
        pool = await self.get_pool()
        if not pool:
            return True
        
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT last_daily_card FROM users WHERE user_id = $1",
                    user_id
                )
                
                if not row or not row['last_daily_card']:
                    return True
                
                # Проверяем, прошло ли 24 часа
                from datetime import datetime, timedelta
                last_card_time = row['last_daily_card']
                if isinstance(last_card_time, str):
                    last_card_time = datetime.fromisoformat(last_card_time)
                
                time_diff = datetime.now() - last_card_time
                return time_diff >= timedelta(hours=24)
        except Exception as e:
            logger.error(f"Ошибка проверки карты дня: {e}")
            return True
    
    async def get_daily_card_data(self, user_id: int):
        """Получить сохраненные данные карты дня"""
        pool = await self.get_pool()
        if not pool:
            return None
        
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT daily_card_data FROM users WHERE user_id = $1",
                    user_id
                )
                
                if row and row['daily_card_data']:
                    import json
                    return json.loads(row['daily_card_data'])
                return None
        except Exception as e:
            logger.error(f"Ошибка получения карты дня: {e}")
            return None
    
    async def save_daily_card(self, user_id: int, card_data: dict):
        """Сохранить данные карты дня пользователя"""
        pool = await self.get_pool()
        if not pool:
            return
        
        try:
            import json
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET last_daily_card = CURRENT_TIMESTAMP, daily_card_data = $1 WHERE user_id = $2",
                    json.dumps(card_data),
                    user_id
                )
        except Exception as e:
            logger.error(f"Ошибка сохранения карты дня: {e}")
    
    def close(self):
        """Закрыть соединение с БД"""
        if self.pool:
            self.pool.close()

