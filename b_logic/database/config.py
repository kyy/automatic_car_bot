import aiosqlite


db_name = 'auto_db'


def database():
    """
    Создаем БД в корне проекта.
    :return:
    """
    return aiosqlite.connect(database=f'../../{db_name}')
