"""
Модуль для работы с PostgreSQL базой данных
Используется при деплое на Railway
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
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица записей на прием
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    slot_id INTEGER,
                    appointment_type TEXT,
                    status TEXT DEFAULT 'pending',
                    payment_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Таблица доступных слотов
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS slots (
                    id SERIAL PRIMARY KEY,
                    date TEXT,
                    time TEXT,
                    is_booked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица новостей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    lang TEXT DEFAULT 'ru',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица карт дня
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_cards (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    card_name TEXT,
                    is_reversed BOOLEAN,
                    date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            logger.info("База данных PostgreSQL инициализирована")
    
    # Убрали синхронные версии - всё асинхронно
    
    # Методы для пользователей
    async def user_exists_async(self, user_id: int) -> bool:
        """Проверить существование пользователя (асинхронно)"""
        pool = await self.get_pool()
        if not pool:
            return False
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT 1 FROM users WHERE user_id = $1",
                user_id
            )
            return row is not None
    
    def user_exists(self, user_id: int) -> bool:
        """Синхронная версия для совместимости (использует созданный pool)"""
        # Проверяем если pool уже создан
        if self.pool:
            import asyncio
            try:
                return asyncio.run(self.user_exists_async(user_id))
            except:
                return False
        return False
    
    async def add_user_async(self, user_id: int, username: str, name: str = None):
        """Добавить пользователя"""
        pool = await self.get_pool()
        if not pool:
            return
        
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (user_id, username, name) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO NOTHING",
                user_id, username, name
            )
    
    def add_user(self, user_id: int, username: str, name: str = None):
        """Синхронная версия"""
        if self.pool:
            import asyncio
            try:
                asyncio.run(self.add_user_async(user_id, username, name))
            except:
                pass
    
    async def get_user_async(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя"""
        pool = await self.get_pool()
        if not pool:
            return None
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1",
                user_id
            )
            if row:
                return dict(row)
        return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Синхронная версия"""
        if self.pool:
            import asyncio
            try:
                return asyncio.run(self.get_user_async(user_id))
            except:
                return None
        return None
    
    async def update_user(self, user_id: int, **kwargs):
        """Обновить данные пользователя"""
        pool = await self.get_pool()
        if not pool:
            return
        
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(kwargs.keys())])
        values = list(kwargs.values()) + [user_id]
        
        query = f"UPDATE users SET {set_clause} WHERE user_id = $1"
        
        async with pool.acquire() as conn:
            await conn.execute(query, *values)
    
    async def update_last_activity(self, user_id: int):
        """Обновить время последней активности"""
        pool = await self.get_pool()
        if not pool:
            return
        
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = $1",
                user_id
            )
    
    def update_last_activity(self, user_id: int):
        """Синхронная версия"""
        import asyncio
        asyncio.run(self.update_last_activity(user_id))
    
    # Методы для слотов
    async def get_available_slots_async(self) -> List[Dict]:
        """Получить доступные слоты"""
        pool = await self.get_pool()
        if not pool:
            return []
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM slots WHERE is_booked = FALSE ORDER BY date, time LIMIT 20"
            )
            return [dict(row) for row in rows]
    
    def get_available_slots(self) -> List[Dict]:
        """Синхронная версия"""
        if self.pool:
            import asyncio
            try:
                return asyncio.run(self.get_available_slots_async())
            except:
                return []
        return []
    
    async def book_slot(self, user_id: int, slot_id: int, appointment_type: str):
        """Забронировать слот"""
        pool = await self.get_pool()
        if not pool:
            return
        
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
    
    def close(self):
        """Закрыть соединение с БД"""
        if self.pool:
            self.pool.close()
    
    # Дополнительные методы для админки
    async def get_stats(self) -> Dict:
        """Получить статистику"""
        pool = await self.get_pool()
        if not pool:
            return {}
        
        async with pool.acquire() as conn:
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            active_today = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE DATE(last_activity) = CURRENT_DATE"
            )
            total_appointments = await conn.fetchval("SELECT COUNT(*) FROM appointments")
            available_slots = await conn.fetchval("SELECT COUNT(*) FROM slots WHERE is_booked = FALSE")
            total_news = await conn.fetchval("SELECT COUNT(*) FROM news")
        
        return {
            'total_users': total_users or 0,
            'active_today': active_today or 0,
            'total_appointments': total_appointments or 0,
            'available_slots': available_slots or 0,
            'total_news': total_news or 0,
            'active_appointments': 0
        }
    
    def get_stats(self) -> Dict:
        """Синхронная версия"""
        import asyncio
        return asyncio.run(self.get_stats())
    
    async def get_all_users(self, limit: int = 20) -> List[Dict]:
        """Получить всех пользователей"""
        pool = await self.get_pool()
        if not pool:
            return []
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT * FROM users ORDER BY created_at DESC LIMIT {limit}"
            )
            return [dict(row) for row in rows]
    
    def get_all_users(self, limit: int = 20) -> List[Dict]:
        """Синхронная версия"""
        import asyncio
        return asyncio.run(self.get_all_users(limit))
    
    async def get_all_appointments(self, limit: int = 20) -> List[Dict]:
        """Получить все записи"""
        pool = await self.get_pool()
        if not pool:
            return []
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT a.*, s.date, s.time FROM appointments a "
                f"JOIN slots s ON a.slot_id = s.id ORDER BY a.created_at DESC LIMIT {limit}"
            )
            return [dict(row) for row in rows]
    
    def get_all_appointments(self, limit: int = 20) -> List[Dict]:
        """Синхронная версия"""
        import asyncio
        return asyncio.run(self.get_all_appointments(limit))
    
    async def get_all_slots(self, limit: int = 20) -> List[Dict]:
        """Получить все слоты"""
        pool = await self.get_pool()
        if not pool:
            return []
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT * FROM slots ORDER BY date, time LIMIT {limit}"
            )
            return [dict(row) for row in rows]
    
    def get_all_slots(self, limit: int = 20) -> List[Dict]:
        """Синхронная версия"""
        import asyncio
        return asyncio.run(self.get_all_slots(limit))
    
    async def get_all_news(self, limit: int = 10) -> List[Dict]:
        """Получить все новости"""
        pool = await self.get_pool()
        if not pool:
            return []
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT * FROM news ORDER BY created_at DESC LIMIT {limit}"
            )
            return [dict(row) for row in rows]
    
    def get_all_news(self, limit: int = 10) -> List[Dict]:
        """Синхронная версия"""
        import asyncio
        return asyncio.run(self.get_all_news(limit))

