import logging

import aiosqlite
import numpy as np
from .config import database
import asyncio
from .user_data_migrations import main as user_data_migrations
from ..constant import FOLDER_PARSE


def br_to_tuple(dictionary: dict[str: [str, str]]) -> list[(str, str)]:
    new = []
    [new.append((key, value[0])) for key, value in dictionary.items()]
    return new


def lenn(items):
    return sum([1 for item in items for sub_item in items[item]])   # noqa


def car_data():
    folder = FOLDER_PARSE
    av_b = np.load(f'{folder}av_brands.npy', allow_pickle=True).item()
    abw_m = np.load(f'{folder}abw_models.npy', allow_pickle=True).item()
    av_m = np.load(f'{folder}av_models.npy', allow_pickle=True).item()
    onliner_m = np.load(f'{folder}onliner_models.npy', allow_pickle=True).item()
    abw_b = np.load(f'{folder}abw_brands.npy', allow_pickle=True).item()
    onliner_b = np.load(f'{folder}onliner_brands.npy', allow_pickle=True).item()
    kufar_b = np.load(f'{folder}kufar_brands.npy', allow_pickle=True).item()
    kufar_m = np.load(f'{folder}kufar_models.npy', allow_pickle=True).item()
    return av_b, abw_m, av_m, onliner_m, abw_b, onliner_b, kufar_b, kufar_m


def l_car_data(av_b, abw_m, av_m, onliner_m, abw_b, onliner_b, kufar_b, kufar_m):
    l_av_b = len(av_b) # noqa
    l_av_m = lenn(av_m)  # noqa
    l_abw_b = len(abw_b) # noqa
    l_abw_m = lenn(abw_m)  # noqa
    l_onliner_b = len(onliner_b) # noqa
    l_onliner_m = lenn(onliner_m) # noqa
    l_kufar_b = len(kufar_b)  # noqa
    l_kufar_m = lenn(kufar_m)  # noqa
    return l_av_b, l_abw_b, l_onliner_b, l_av_m, l_abw_m, l_onliner_m, l_kufar_m, l_kufar_b


def checking_null(*args):   # проверяем все ли файлы с данными
    xxx = [*args]
    return all([x > 0 for x in xxx])


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
        logging.info('tables brands and models are created')
    except aiosqlite.Error as e:
        logging.error(f'{e}')


async def av_brands(db, av_b, l_av_b):
    """
    Заполняем или обновляем таблицу brands: id, [unique], av_by,
    :param db: инструкция к БД
    :return: None
    """
    cursor_av_b = await db.execute("""select [unique], id  from brands """)
    av_bd = await cursor_av_b.fetchall()
    l_av_bd = len(av_bd)
    if l_av_bd == 0:
        await db.executemany("""
            INSERT INTO brands([unique], av_by) 
            VALUES(?, ?)""", br_to_tuple(av_b))    # noqa заполняем пустую таблицу
        await db.commit()
        logging.info('av <- brands is comitted')
    else:
        logging.info(f'av <- brands: {l_av_bd}/{l_av_b}')
        update = []
        update_insert = []
        for item in av_b:
            if item not in [i[0] for i in av_bd]:
                update_insert.append((item, av_b[item][0]))
        await db.executemany("""
            REPLACE INTO brands([unique], av_by) 
            VALUES(?, ?)""", update_insert)     # вставляем новые бренды
        for item in av_bd:
            if item[0] in av_b:
                update.append((item[1], item[0], av_b[item[0]][0]))
            else:
                await db.execute(f"""
                    DELETE FROM brands 
                    WHERE id={item[1]}""")    # удаляем неактуальные бренды
        await db.executemany("""
            REPLACE INTO brands(id, [unique], av_by) 
            VALUES(?, ?, ?)""", update)      # обновляем все бренды
        await db.commit()
        logging.info('av <- brands is comitted')
        await asyncio.sleep(0.1)
        if l_av_b != l_av_bd:
            logging.info(f'av <- brands added: {l_av_b-l_av_bd}')


async def av_models(db, av_m, l_av_m):
    """
    Заполняем или обновляем таблицу models: id, brand_id, [unique], av_by,
    :param db: инструкция к БД
    :return: None
    """
    cursor_av_b = await db.execute("""
        SELECT id, [unique] FROM brands;""")
    cursor_av_m = await db.execute("""
        SELECT id, [unique], brand_id FROM models;""")
    cursor_av_bm = await db.execute("""
        SELECT brands.[unique], models.[unique], models.id FROM brands
        INNER JOIN models ON brands.id = models.brand_id
                """)
    av_bd_b = await cursor_av_b.fetchall()
    av_bd_m = await cursor_av_m.fetchall()
    av_bd_bm = await cursor_av_bm.fetchall()
    l_av_bd_m = len(av_bd_m)
    models_list = []
    models_list_update = []
    models_list_insert = []
    brand_dict = {}

    for brand in av_bd_b:
        brand_dict.update({brand[1]: brand[0]})

    for item in av_bd_b:
        models = av_m[item[1]]          # noqa
        for model in models:
            models_list.append((item[0], model, models[model][0]))

    if l_av_bd_m == 0:
        await db.executemany(
            "INSERT INTO models(brand_id, [unique], av_by) "
            "VALUES(?, ?, ?);", models_list)
        await db.commit()
        logging.info('av <- models is comitted')
    else:
        logging.info(f'av <- models: {l_av_bd_m}/{l_av_m}')

        for brand_model in av_bd_bm:
            if brand_model[1] not in av_m[brand_model[0]]:
                await db.execute(f"""
                DELETE FROM models
                WHERE id={brand_model[2]}
                """)    # чистим базу от неактуальных моделей
        for brand in av_m:
            for model in av_m[brand]:
                if (brand, model) not in [i[0:2] for i in av_bd_bm]:
                    models_list_insert.append((brand_dict[brand], model, av_m[brand][model][0]))
                else:
                    for item in av_bd_m:
                        if item[1:3] == (model, brand_dict[brand]):
                            models_list_update.append((item[0], brand_dict[brand], model, av_m[brand][model][0]))
        await db.executemany(
            "INSERT INTO models(brand_id, [unique], av_by) "
            "VALUES(?, ?, ?);", models_list_insert)   # записываем новые модели
        await db.executemany(
            "REPLACE INTO models(id, brand_id, [unique], av_by) "
            "VALUES(?, ?, ?, ?);", models_list_update)    # обновляем модели моделей
        await db.commit()
        logging.info('av <- brands is comitted')
        await asyncio.sleep(0.1)
        if l_av_m != l_av_bd_m:
            logging.info(f'av <- brands addied: {l_av_m - l_av_bd_m}')


async def add_brand(db, brand_data: dict[str: list[str, str], ], set_row: str, index: int):
    """
    Добавляет бренды в соответствующий столбец
    :param db: инструкция к БД
    :param brand_data: данные (словарь содержащий бренды, cо списком параметров: id, slug)
    :param set_row: имя столбца куда добавляем данные
    :param index: id=0, slug=1
    :return: None
    """
    cursor_av_b = await db.execute("""SELECT id, [unique] FROM brands;""")
    av_bd_b = await cursor_av_b.fetchall()
    for brand in brand_data:
        if brand in [item[1] for item in av_bd_b]:
            await db.execute(f"""
                UPDATE brands
                SET {set_row} = '{brand_data[brand][index]}' 
                WHERE [unique] = '{brand}';
                """)
    await db.commit()
    logging.info(f'{set_row} <- brands is comitted')


async def add_model(db, model_data: dict[str: dict[str: list[str, str, str], ], ], set_row: str, index: int):
    """
        Добавляет модели в соответствующий столбец
        :param db: инструкция к БД
        :param model_data: данные (словарь содержащий модели, cо списком параметров: id, name, slug)
        :param set_row: имя столбца куда добавляем данные
        :param index: id=0, name=1, slug=2
        :return: None
        """
    cursor_av_m = await db.execute(f"""
            select brands.[unique], models.[unique] from brands 
            inner join models on brands.id = models.brand_id 
        """)
    av_bd_m = await cursor_av_m.fetchall()
    for brand in model_data:
        for model in model_data[brand]:
            if (brand, model) in av_bd_m:
                await db.execute(f'''
                    UPDATE models 
                    SET {set_row} = '{model_data[brand][model][index]}' 
                    WHERE [unique] = "{model}";
                    ''')
    await db.commit()
    logging.info(f'{set_row} <- models is comitted')


async def delete_dublicates(db, table: str):
    """
    Удаляем дубликаты в таблице с уникальным id
    :param db: инструкция к БД
    :param table: имя таблицы
    :return: None
    """
    cursor = await db.execute(f"""SELECT * FROM {table}""")
    rows = await cursor.fetchall()
    unique_list = []

    for row in rows:
        if row[1::] not in [i[1::] for i in unique_list]:
            unique_list.append(row)
        else:
            await db.execute(f"""
                DELETE FROM {table}
                WHERE id={row[0]}
                ORDER BY DATE 
            """)
            logging.info(f'dublicate: {table}: {row}')
    await db.commit()


async def main(db: database()):
    """
    Выполняем сценарий по созданию и наполнению БД
    :return: None
    """
    av_b, abw_m, av_m, onliner_m, abw_b, onliner_b, kufar_b, kufar_m = car_data()
    l_av_b, l_abw_b, l_onliner_b, l_av_m, l_abw_m, l_onliner_m, l_kufar_m, l_kufar_b = l_car_data(av_b, abw_m, av_m, onliner_m, abw_b, onliner_b, kufar_b, kufar_m)
    async with db:
        if checking_null(l_av_b, l_abw_b, l_onliner_b, l_av_m, l_abw_m, l_onliner_m, l_kufar_m, l_kufar_b):
            await create_tables(db)
            await user_data_migrations(db)
            await av_brands(db, av_b, l_av_b),
            await av_models(db, av_m, l_av_m),
            await add_brand(db, abw_b, 'abw_by', 1),
            await add_brand(db, onliner_b, 'onliner_by', 0),
            await add_brand(db, kufar_b, 'kufar_by', 0),
            await add_model(db, abw_m, 'abw_by', 2),
            await add_model(db, onliner_m, 'onliner_by', 0),
            await add_model(db, kufar_m, 'kufar_by', 0),
            await delete_dublicates(db, 'brands')
            await delete_dublicates(db, 'models')
        else:
            logging.info('Присутствуют пустые словари в папке parse')

