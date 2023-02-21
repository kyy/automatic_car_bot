import aiosqlite


db_name = 'auto_db'
def database():
    return aiosqlite.connect(database=f'../../{db_name}')


