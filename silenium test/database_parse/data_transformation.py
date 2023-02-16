import asyncio
import aiosqlite
import numpy as np
from tqdm import tqdm


def br_to_tuple(dictionary: dict[str: [str, str]]) -> list[(str, str)]:
    new = {}
    [new.update({key: value[0]}) for key, value in dictionary.items()]
    return list(new.items())


abw_m = np.load('abw_models.npy', allow_pickle=True).item()
av_m = np.load('av_models.npy', allow_pickle=True).item()
onliner_m = np.load('onliner_models.npy', allow_pickle=True).item()
abw_b = np.load('abw_brands.npy', allow_pickle=True).item()
av_b = np.load('av_brands.npy', allow_pickle=True).item()
onliner_b = np.load('onliner_brands.npy', allow_pickle=True).item()
l_av_b = len(av_b)


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


async def av_brands(db):
    cursor = await db.execute(f"select [unique], id  from brands ")
    av_bd = await cursor.fetchall()
    l_av_bd = len(av_bd)
    if l_av_bd == 0:
        await db.executemany("""INSERT INTO brands([unique], av_by) VALUES(?, ?)""", br_to_tuple(av_b))
        await db.commit()
    else:
        print(f'Кол-во брендов: БД/av.by  {l_av_bd}/{l_av_b}')
        update = []
        for item in tqdm(av_bd):
            if item[0] in av_b:
                update.append((item[1], item[0], av_b[item[0]][0]))
        await db.executemany("""REPLACE INTO brands(id, [unique], av_by) VALUES(?, ?, ?)""", update)
        await db.commit()
        print(f'Данные обновлены brands([unique], av_by)')
        if l_av_b != l_av_bd:
            print(f'Добавлено - {l_av_b-l_av_bd}')



async def main():
    async with aiosqlite.connect('test_db') as db:
        await asyncio.gather(
            #create_tables(db),
            av_brands(db),
        )


if __name__ == '__main__':
    asyncio.run(main())