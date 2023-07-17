import asyncio
import aiosqlite
from .config import database


async def create_tables(db):
    try:
        await db.executescript("""
            CREATE TABLE user(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            tel_id TEXT (0, 128)
            );
            CREATE TABLE udata(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            user_id INTEGER REFERENCES user (id) ON DELETE CASCADE, 
            search_param TEXT (0, 64),
            is_active INT DEFAULT 1
            )""")
        await db.commit()
        print('+ user, udata успешно созданы')
    except aiosqlite.Error:
        print('---> user, udata уже существуют')


async def main(db: database()):
    await create_tables(db)
