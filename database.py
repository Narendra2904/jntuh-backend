import aiosqlite
import json

DB_NAME = "results.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS results (
                hallTicket TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        await db.commit()


async def get_result_from_db(htno):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT data FROM results WHERE hallTicket = ?",
            (htno,)
        )
        row = await cursor.fetchone()
        return json.loads(row[0]) if row else None


async def save_result_to_db(htno, data):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO results VALUES (?, ?)",
            (htno, json.dumps(data))
        )
        await db.commit()
