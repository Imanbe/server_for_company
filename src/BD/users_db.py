from typing import Tuple, List
import aiosqlite

DB_PATH = "users.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                is_excluded BOOLEAN NOT NULL DEFAULT 0
            )
        """
        )
        await db.commit()


async def add_user(user_id: str, user_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        )
        if not await cursor.fetchone():
            await db.execute(
                "INSERT INTO users (user_id, user_name, is_excluded) VALUES (?, ?, 0)",
                (user_id, user_name),
            )
            await db.commit()


# Асинхронная функция для получения списка доступных пользователей (не исключённых)
async def get_available_users() -> List[Tuple[str, str]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, user_name FROM users WHERE is_excluded = 0"
        )
        return await cursor.fetchall()


async def reset_excluded_users():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_excluded = 0")
        await db.commit()


async def distribute_tasks() -> Tuple[str, str]:
    async with aiosqlite.connect(DB_PATH) as db:
        # Одновременно выбираем и исключаем одного пользователя
        cursor = await db.execute(
            """
            UPDATE users 
            SET is_excluded = 1 
            WHERE user_id IN (
                SELECT user_id 
                FROM users 
                WHERE is_excluded = 0 
                ORDER BY RANDOM() 
                LIMIT 1
            )
            RETURNING user_id, user_name
        """
        )
        result = await cursor.fetchone()

        if result is None:  # Нет доступных пользователей
            print("Все пользователи были исключены, начинаем новый цикл...")
            await db.execute("UPDATE users SET is_excluded = 0")
            cursor = await db.execute(
                """
                UPDATE users 
                SET is_excluded = 1 
                WHERE user_id IN (
                    SELECT user_id 
                    FROM users 
                    WHERE is_excluded = 0 
                    ORDER BY RANDOM() 
                    LIMIT 1
                )
                RETURNING user_id, user_name
            """
            )
            result = await cursor.fetchone()

        await db.commit()
        return result  # (user_id, user_name)
