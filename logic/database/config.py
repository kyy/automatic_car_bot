import logging

import aiosqlite


db_name = 'auto_db'
backup_db_name = 'backup_auto_db'


def database():
    """
    Создаем БД в корне проекта.
    :return:
    """
    return aiosqlite.connect(database=f'{db_name}')

def backup_database():
    return aiosqlite.connect(database=f'{backup_db_name}')


async def backup_db():
    async with database() as db:
        async with backup_database() as db2:
            await db.backup(db2)
            logging.info('Database copied!')


class Connection:

    async def __aenter__(self):
        self.conn = database()
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return await self.conn.close()
