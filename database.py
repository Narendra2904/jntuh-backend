import aiosqlite
import os

DB_PATH = "results.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS results (
            hall_ticket TEXT PRIMARY KEY,
            data TEXT
        )
        """)
        await db.commit()


async def get_result_from_db(htno: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT data FROM results WHERE hall_ticket = ?",
            (htno,)
        )
        row = await cursor.fetchone()
        return None if not row else row[0]


async def save_result_to_db(htno: str, data):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO results VALUES (?, ?)",
            (htno, str(data))
        )
        await db.commit()
