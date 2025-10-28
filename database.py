"""
Модуль для работы с базой данных
Поддерживает PostgreSQL (Railway) и SQLite (fallback)
"""
import aiosqlite
import asyncpg
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        self.conn = None
        # Проверяем, используется ли PostgreSQL из Railway
        self.database_url = os.getenv("DATABASE_URL", None)
        self.use_postgres = self.database_url is not None
    
    async def get_connection(self):
        """Получить соединение с БД"""
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
        return self.conn
    
    async def init_db(self):
        """Инициализация базы данных"""
        try:
            conn = await self.get_connection()
            
            # Таблица пользователей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    slot_id INTEGER,
                    appointment_type TEXT,
                    status TEXT DEFAULT 'pending',
                    payment_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (slot_id) REFERENCES slots(id)
                )
            """)
            
            # Таблица доступных слотов
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    time TEXT,
                    is_booked INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица новостей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    lang TEXT DEFAULT 'ru',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица карт дня
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    card_name TEXT,
                    is_reversed INTEGER,
                    date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            await conn.commit()
            logger.info("База данных инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
    
    def init_db(self):
        """Синхронная версия инициализации БД"""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Таблица пользователей
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    slot_id INTEGER,
                    appointment_type TEXT,
                    status TEXT DEFAULT 'pending',
                    payment_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (slot_id) REFERENCES slots(id)
                )
            """)
            
            # Таблица доступных слотов
            conn.execute("""
                CREATE TABLE IF NOT EXISTS slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    time TEXT,
                    is_booked INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица новостей
            conn.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    lang TEXT DEFAULT 'ru',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица карт дня
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    card_name TEXT,
                    is_reversed INTEGER,
                    date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("База данных инициализирована (синхронная версия)")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
    
    # Методы для пользователей
    async def user_exists(self, user_id: int) -> bool:
        """Проверить существование пользователя"""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT 1 FROM users WHERE user_id = ?",
            (user_id,)
        )
        return await cursor.fetchone() is not None
    
    def user_exists(self, user_id: int) -> bool:
        """Синхронная версия"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    async def add_user(self, user_id: int, username: str, name: str = None):
        """Добавить пользователя"""
        conn = await self.get_connection()
        await conn.execute(
            "INSERT INTO users (user_id, username, name) VALUES (?, ?, ?)",
            (user_id, username, name)
        )
        await conn.commit()
    
    def add_user(self, user_id: int, username: str, name: str = None):
        """Синхронная версия"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO users (user_id, username, name) VALUES (?, ?, ?)",
            (user_id, username, name)
        )
        conn.commit()
        conn.close()
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя"""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(zip([col[0] for col in cursor.description], row))
        return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Синхронная версия"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            columns = ['user_id', 'username', 'name', 'birth_date', 'birth_time', 
                     'birth_place', 'photo', 'rating', 'language', 'created_at', 'last_activity']
            return dict(zip(columns, row))
        return None
    
    async def update_user(self, user_id: int, **kwargs):
        """Обновить данные пользователя"""
        conn = await self.get_connection()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        await conn.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ?",
            values
        )
        await conn.commit()
    
    def update_last_activity(self, user_id: int):
        """Обновить время последней активности (синхронная версия)"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        conn.close()
    
    # Методы для слотов
    async def get_available_slots(self) -> List[Dict]:
        """Получить доступные слоты"""
        conn = await self.get_connection()
        cursor = await conn.execute(
            "SELECT * FROM slots WHERE is_booked = 0 ORDER BY date, time LIMIT 20"
        )
        rows = await cursor.fetchall()
        columns = ['id', 'date', 'time', 'is_booked', 'created_at']
        return [dict(zip(columns, row)) for row in rows]
    
    def get_available_slots(self) -> List[Dict]:
        """Синхронная версия"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM slots WHERE is_booked = 0 ORDER BY date, time LIMIT 20"
        )
        rows = cursor.fetchall()
        conn.close()
        columns = ['id', 'date', 'time', 'is_booked', 'created_at']
        return [dict(zip(columns, row)) for row in rows]
    
    async def book_slot(self, user_id: int, slot_id: int, appointment_type: str):
        """Забронировать слот"""
        conn = await self.get_connection()
        await conn.execute(
            "INSERT INTO appointments (user_id, slot_id, appointment_type) VALUES (?, ?, ?)",
            (user_id, slot_id, appointment_type)
        )
        await conn.execute(
            "UPDATE slots SET is_booked = 1 WHERE id = ?",
            (slot_id,)
        )
        await conn.commit()
    
    def close(self):
        """Закрыть соединение с БД"""
        if self.conn:
            self.conn.close()
    
    # Дополнительные методы для админки
    def get_stats(self) -> Dict:
        """Получить статистику"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM users WHERE DATE(last_activity) = DATE('now')")
        active_today = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM appointments")
        total_appointments = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM slots WHERE is_booked = 0")
        available_slots = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM news")
        total_news = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_today': active_today,
            'total_appointments': total_appointments,
            'available_slots': available_slots,
            'total_news': total_news,
            'active_appointments': 0
        }
    
    def get_all_users(self, limit: int = 20) -> List[Dict]:
        """Получить всех пользователей"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['user_id', 'username', 'name', 'birth_date', 'birth_time',
                  'birth_place', 'photo', 'rating', 'language', 'created_at', 'last_activity']
        return [dict(zip(columns, row)) for row in rows]
    
    def get_all_appointments(self, limit: int = 20) -> List[Dict]:
        """Получить все записи"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT a.*, s.date, s.time FROM appointments a "
            "JOIN slots s ON a.slot_id = s.id ORDER BY a.created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_slots(self, limit: int = 20) -> List[Dict]:
        """Получить все слоты"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM slots ORDER BY date, time LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'date', 'time', 'is_booked', 'created_at']
        return [dict(zip(columns, row)) for row in rows]
    
    def get_all_news(self, limit: int = 10) -> List[Dict]:
        """Получить все новости"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM news ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'title', 'content', 'lang', 'created_at']
        return [dict(zip(columns, row)) for row in rows]

