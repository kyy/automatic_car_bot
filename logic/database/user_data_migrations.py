from .config import database


async def create_tables(db):
    try:
        await db.executescript("""
            CREATE TABLE user(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            tel_id TEXT (0, 128),
            vip INT DEFAULT 0
            );
            
            CREATE TABLE udata(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            user_id INTEGER REFERENCES user (id) ON DELETE CASCADE, 
            search_param TEXT (0, 64),
            is_active INT DEFAULT 1
            );
            
            CREATE TABLE ucars(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            user_id INTEGER REFERENCES user (id) ON DELETE CASCADE,
            url TEXT (0, 128),
            price INTEGER (0, 16)
            )
            """)
        await db.commit()
        print('+ user, udata успешно созданы')
    except Exception as e:
        print(e, '---> user, udata уже существуют')


async def main(db: database()):
    await create_tables(db)
