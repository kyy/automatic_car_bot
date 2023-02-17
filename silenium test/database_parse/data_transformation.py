import asyncio
import aiosqlite
import numpy as np



def br_to_tuple(dictionary: dict[str: [str, str]]) -> list[(str, str)]:
    new = []
    return [new.append((key, value[0])) for key, value in dictionary.items()]


def lenn(items):
    return sum([1 for item in items for sub_item in items[item]])


abw_m = np.load('abw_models.npy', allow_pickle=True).item()
av_m = np.load('av_models.npy', allow_pickle=True).item()
onliner_m = np.load('onliner_models.npy', allow_pickle=True).item()
abw_b = np.load('abw_brands.npy', allow_pickle=True).item()
av_b = np.load('av_brands.npy', allow_pickle=True).item()
onliner_b = np.load('onliner_brands.npy', allow_pickle=True).item()
l_av_b = len(av_b)      # ---> всех брендов в av.by
l_av_m = lenn(av_m)     # ---> всех моделей av.by

print(abw_b)


async def create_tables(db):
    """
    Создаем 2 таблицы brands и models
    + с av.by принимаем как эталонные
    :param db: инструкция к БД
    :return: None
    """
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
        print('+ brands, models успешно созданы')
    except aiosqlite.Error:
        print('---> brands, models уже существуют')


async def av_brands(db):
    """
    Заполняем или обновляем таблицу brands: id, [unique], av_by,
    :param db: инструкция к БД
    :return: None
    """
    cursor_av_b = await db.execute(f"select [unique], id  from brands ")
    av_bd = await cursor_av_b.fetchall()
    l_av_bd = len(av_bd)
    if l_av_bd == 0:
        await db.executemany("""INSERT INTO brands([unique], av_by) VALUES(?, ?)""", br_to_tuple(av_b))
        await db.commit()
        print(f'+ добавлены brands([unique], av_by)')
    else:
        print(f'---> брендов: БД/av.by  {l_av_bd}/{l_av_b}')
        update = []
        for item in av_bd:
            update.append((item[1], item[0], av_b[item[0]][0]))
        await db.executemany("""REPLACE INTO brands(id, [unique], av_by) VALUES(?, ?, ?)""", update)
        await db.commit()
        print(f'+ обновлены brands([unique], av_by)')
        await asyncio.sleep(0.1)
        if l_av_b != l_av_bd:
            print(f'Добавлено - {l_av_b-l_av_bd}')


async def models_part_db(db):
    """
    Заполняем или обновляем таблицу models: id, brand_id, [unique], av_by,
    :param db: инструкция к БД
    :return: None
    """
    cursor_av_b = await db.execute("SELECT id, [unique] FROM brands;")
    cursor_av_m = await db.execute("SELECT id, [unique] FROM models;")
    av_bd_b = await cursor_av_b.fetchall()
    av_bd_m = await cursor_av_m.fetchall()
    l_av_bd_m = len(av_bd_m)
    models_list = []
    for item in av_bd_b:
        models = av_m[item[1]]
        for model in models:
            models_list.append((item[0], model, models[model][0]))
    if l_av_bd_m == 0:
        await db.executemany(
            "INSERT INTO models(brand_id, [unique], av_by) VALUES(?, ?, ?);", models_list)
        await db.commit()
        print(f'+ добавлены models([unique], av_by)')
    else:
        print(f'---> моделей: БД/av.by  {l_av_bd_m}/{l_av_m}')
        models_list_update = []
        for i in av_bd_m:
            for j in models_list:
                if i[1] == j[1]:
                    models_list_update.append((i[0], )+j)
        await db.executemany(
            "REPLACE INTO models(id, brand_id, [unique], av_by) VALUES(?, ?, ?, ?);", models_list_update)
        await db.commit()
        print(f'+ обновлены models([unique], av_by)')
        await asyncio.sleep(0.1)
        if l_av_m != l_av_bd_m:
            print(f'Добавлено - {l_av_m - l_av_bd_m}')


async def add_brand(db, brand_data: dict[str: [str, str]], set_row: str, index: int):
    """
    Добавляет модели в соответствующий столбец
    :param db: инструкция к БД
    :param brand_data: данные (словарь содержащий бренды, cо списком параметров: id, slug)
    :param set_row: имя столбца куда добавляем данные
    :param index: id: index=0, slug: index=1
    :return: None
    """
    cursor_av_b = await db.execute("SELECT id, [unique] FROM brands;")
    av_bd_b = await cursor_av_b.fetchall()
    for brand in brand_data:
        if brand in [item[1] for item in av_bd_b]:
            await db.execute(f"""
            UPDATE brands
            SET {set_row} = '{brand_data[brand][index]}'
            WHERE [unique] = '{brand}';
            """)
    await db.commit()
    print(f'+ brands - {set_row}')


async def main(db_name='test_db'):
    f"""
    Выполняем сценарий по созданию и наполнению БД {db_name}
    :return: None
    """
    try:
        async with aiosqlite.connect(db_name) as db:
            await asyncio.gather(
                create_tables(db),
                av_brands(db),
                models_part_db(db),
                add_brand(db, abw_b, 'abw_by', 1),
                add_brand(db, onliner_b, 'onliner_by', 0),
            )
    except aiosqlite.Error as e:
        print(e, f'\nНе удалось подключиться к БД {db_name}')


if __name__ == '__main__':
    asyncio.run(main())
