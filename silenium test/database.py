import asyncio
import aiosqlite
import numpy as np
from tqdm import tqdm

source = 'https://aiosqlite.omnilib.dev/en/stable/'


# создаем таблицы брендов и связаных с ними моделей
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
            [unique] TEXT (0, 32) NOT NULL,
            av_by TEXT (0, 32) UNIQUE,
            abw_by TEXT (0, 32) UNIQUE
            )""")
        await db.commit()
        print('Таблицы - brands, models успешно созданы')
    except Exception as e:
        print(e, 'Таблицы уже существуют')


brands_part = np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item()
brands_part_list = list(brands_part.items())


# добавляем в базу данных бренды и av.by идентификаторы
async def brands_part_db(db):
    try:
        await db.executemany("INSERT INTO brands([unique], av_by) VALUES(?, ?);", brands_part_list)
        await db.commit()
    except Exception as e:
        print(e, 'Такие данные уже существуют')


# добавляем в базу данных модели и av.by идентификаторы
async def models_part_db(db):
    cursor = await db.execute("SELECT id, [unique] FROM brands;")
    rows = await cursor.fetchall()
    models_list = []
    for item in rows:
        models = np.load(f'base_data_av_by/models_part_url/{item[1]}.npy', allow_pickle=True).item()  # открываем модели
        model_list = list(models.items())      # преобразуем в список кортеджей
        for model in model_list:
            new = item[0:1] + model     # конкатенация кортеджей со срезом, удаляем бренд
            models_list.append(new)
    await db.executemany("INSERT INTO models(brand_id, [unique], av_by) VALUES(?, ?, ?);", models_list)
    await db.commit()


brands_abw = np.load('base_data_abw_by/brands.npy', allow_pickle=True).item()
for i in brands_abw:
    if brands_abw[i] == '':
        del brands_abw[i]
brands_abw_list = list(brands_abw.items())
print(brands_abw_list)


async def brands_part_db_abw(db):
    for brand in tqdm(brands_abw_list):
        await db.execute(f"UPDATE brands "
                        f"SET abw_by = '{brand[1]}'"
                        f"WHERE [unique] = '{brand[0]}';")
    await db.commit()


async def main():
    async with aiosqlite.connect('auto_db') as db:
        await asyncio.gather(
            # create_tables(db),
            # brands_part_db(db),
            # models_part_db(db),
            brands_part_db_abw(db),
        )


if __name__ == '__main__':
    asyncio.run(main())

