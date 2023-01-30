import asyncio
import aiosqlite


source = 'https://aiosqlite.omnilib.dev/en/stable/'


async def create_tables(db):
    try:
        await db.execute("""
        CREATE TABLE brands(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            [unique] TEXT (0, 32) UNIQUE NOT NULL,
            av_by TEXT (0, 32) UNIQUE,
            abw_by TEXT (0, 32) UNIQUE
            )""")

        await db.execute("""
        CREATE TABLE models(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER REFERENCES brands (id) ON DELETE CASCADE,
            [unique] TEXT (0, 32) UNIQUE NOT NULL,
            av_by TEXT (0, 32) UNIQUE,
            abw_by TEXT (0, 32) UNIQUE
            )""")
        await db.commit()
        print('Таблицы - brands, models успешно созданы')
    except Exception as e:
        print(e, 'Таблицы уже существуют')


async def main():
    async with aiosqlite.connect('auto_db') as db:
        await asyncio.gather(create_tables(db),
                             )


if __name__ == '__main__':
    asyncio.run(main())
