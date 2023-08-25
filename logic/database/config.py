import aiosqlite


db_name = 'auto_db'


def database():
    """
    Создаем БД в корне проекта.
    :return:
    """
    return aiosqlite.connect(database=f'{db_name}')


class Connection:

    async def __aenter__(self):
        self.conn = database()
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return await self.conn.close()
