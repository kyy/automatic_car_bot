import aiosqlite


def database():
    return aiosqlite.connect(database='../auto_db')


