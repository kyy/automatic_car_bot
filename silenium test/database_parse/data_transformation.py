import asyncio
import aiosqlite
import numpy as np
from tqdm import tqdm

def to_tuple(dictionary):
    new = {}
    for key, value in dictionary.items():
        new.update({key: value[0]})
    new = list(new.items())
    return new

abw_m = np.load('abw_models.npy', allow_pickle=True).item()
av_m = np.load('av_models.npy', allow_pickle=True).item()
onliner_m = np.load('onliner_models.npy', allow_pickle=True).item()
abw_b = np.load('abw_brands.npy', allow_pickle=True).item()
av_b = np.load('av_brands.npy', allow_pickle=True).item()
onliner_b = np.load('onliner_brands.npy', allow_pickle=True).item()



source = 'https://aiosqlite.omnilib.dev/en/stable/'


async def create_tables(db):
    try:
        await db.executescript("""
            CREATE TABLE brands(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            [unique] TEXT (0, 32) NOT NULL, 
            av_by TEXT (0, 32), 
            abw_by TEXT (0, 32), 
            onliner_by TEXT (0, 32),
            kufar_by TEXT (0, 32)
            );
            CREATE TABLE models(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            brand_id INTEGER REFERENCES brands (id) ON DELETE CASCADE, 
            [unique] TEXT (0, 32) NOT NULL, 
            av_by TEXT (0, 32), 
            abw_by TEXT (0, 32), 
            onliner_by TEXT (0, 32),
            kufar_by TEXT (0, 32)
            )""")
        await db.commit()
        print('Таблицы - brands, models успешно созданы')
    except Exception as e:
        print(e, '\nТаблицы уже существуют')


# async def av_brands(db):
#     await db.executemany("INSERT INTO brands([unique], av_by) VALUES(?, ?);", ---)
#     await db.commit()


async def main():
    async with aiosqlite.connect('test_db') as db:
        await asyncio.gather(
            #create_tables(db),
            #av_brands(db),
        )


if __name__ == '__main__':
    asyncio.run(main())