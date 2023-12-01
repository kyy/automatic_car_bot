import logging
import numpy as np
from .config import database
import asyncio
from .user_data_migrations import create
from ..constant import FOLDER_PARSE


def br_to_tuple(dictionary: dict[str: [str, str]]) -> list[(str, str)]:
    new = []
    [new.append((key, value[0])) for key, value in dictionary.items()]
    return new


def lenn(items):
    return sum([1 for item in items for sub_item in items[item]])  # noqa


def car_data():
    def o(name: str):
        folder = FOLDER_PARSE
        return np.load(f'{folder}{name}.npy', allow_pickle=True).item()

    av_b = o('av_brands')
    abw_m = o('abw_models')
    av_m = o('av_models')
    onliner_m = o('onliner_models')
    abw_b = o('abw_brands')
    onliner_b = o('onliner_brands')
    kufar_b = o('kufar_brands')
    kufar_m = o('kufar_models')

    return dict(
        av_b=av_b, abw_m=abw_m, av_m=av_m, onliner_m=onliner_m, abw_b=abw_b,
        onliner_b=onliner_b, kufar_b=kufar_b, kufar_m=kufar_m,
    )


def l_car_data(**kwargs):
    l_av_b = len(kwargs["av_b"])
    l_av_m = lenn(kwargs["av_m"])
    l_abw_b = len(kwargs["abw_b"])
    l_abw_m = lenn(kwargs["abw_m"])
    l_onliner_b = len(kwargs["onliner_b"])
    l_onliner_m = lenn(kwargs["onliner_m"])
    l_kufar_b = len(kwargs["kufar_b"])
    l_kufar_m = lenn(kwargs["kufar_m"])
    return dict(
        l_av_b=l_av_b, l_abw_b=l_abw_b, l_onliner_b=l_onliner_b, l_av_m=l_av_m, l_abw_m=l_abw_m,
        l_onliner_m=l_onliner_m, l_kufar_m=l_kufar_m, l_kufar_b=l_kufar_b,
    )


def checking_null(**kwargs):  # проверяем все ли файлы с данными
    xxx = [i for i in kwargs.values()]
    return all([x > 0 for x in xxx])


async def av_brands(db, av_b, l_av_b):
    """
    Заполняем или обновляем таблицу brands: id, [unique], av_by,
    :param l_av_b:
    :param av_b:
    :param db: инструкция к БД
    :return: None
    """
    cursor_av_b = await db.execute("""select [unique], id  from brands """)
    av_bd = await cursor_av_b.fetchall()
    l_av_bd = len(av_bd)
    if l_av_bd == 0:
        await db.executemany("""
            INSERT INTO brands([unique], av_by) VALUES(?, ?)""", br_to_tuple(av_b))  # noqa заполняем пустую таблицу
        await db.commit()
        logging.info('av_by <- brands is comitted')
    else:
        logging.info(f'av_by <- brands: {l_av_bd}/{l_av_b}')
        update = []
        update_insert = []
        for item in av_b:
            if item not in [i[0] for i in av_bd]:
                update_insert.append((item, av_b[item][0]))
        await db.executemany("""
            REPLACE INTO brands([unique], av_by) VALUES(?, ?)""", update_insert)  # вставляем новые бренды
        for item in av_bd:
            if item[0] in av_b:
                update.append((item[1], item[0], av_b[item[0]][0]))
            else:
                await db.execute("""DELETE FROM brands WHERE id=$s""", (item[1],), )  # удаляем неактуальные бренды
        await db.executemany("""
            REPLACE INTO brands(id, [unique], av_by) VALUES(?, ?, ?)""", update)  # обновляем все бренды
        await db.commit()
        logging.info('av_by <- brands is comitted')
        await asyncio.sleep(0.1)
        if l_av_b != l_av_bd:
            logging.info(f'av_by <- brands result: {l_av_b - l_av_bd}')


async def av_models(db, av_m: dict, l_av_m: int):
    """
    Заполняем или обновляем таблицу models: id, brand_id, [unique], av_by,
    :param l_av_m:
    :param av_m:
    :param db: инструкция к БД
    :return: None
    """
    cursor_av_b = await db.execute("""SELECT id, [unique] FROM brands;""")
    cursor_av_m = await db.execute("""SELECT id, [unique], brand_id FROM models;""")
    cursor_av_bm = await db.execute(
        """SELECT brands.[unique], models.[unique], models.id 
        FROM brands INNER JOIN models ON brands.id = models.brand_id""")
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
        models = av_m[item[1]]  # noqa
        for model in models:
            models_list.append((item[0], model, models[model][0]))

    if l_av_bd_m == 0:
        await db.executemany(
            "INSERT INTO models(brand_id, [unique], av_by) "
            "VALUES(?, ?, ?);", models_list)
        await db.commit()
        logging.info('av_by <- models is comitted')
    else:
        logging.info(f'av_by <- models: {l_av_bd_m}/{l_av_m}')

        for brand_model in av_bd_bm:
            if brand_model[1] not in av_m[brand_model[0]]:
                # чистим базу от неактуальных моделей
                await db.execute("""DELETE FROM models WHERE id=$s""", (brand_model[2],))
        for brand in av_m:
            for model in av_m[brand]:
                if (brand, model) not in [i[0:2] for i in av_bd_bm]:
                    models_list_insert.append((brand_dict[brand], model, av_m[brand][model][0],))
                else:
                    for item in av_bd_m:
                        if item[1:3] == (model, brand_dict[brand]):
                            models_list_update.append((item[0], brand_dict[brand], model, av_m[brand][model][0]))
        # записываем новые модели
        await db.executemany(
            "INSERT INTO models(brand_id, [unique], av_by) VALUES(?, ?, ?);", models_list_insert)
        # обновляем модели моделей
        await db.executemany(
            "REPLACE INTO models(id, brand_id, [unique], av_by) VALUES(?, ?, ?, ?);", models_list_update)
        await db.commit()
        logging.info('av_by <- models is comitted')
        await asyncio.sleep(0.1)
        if l_av_m != l_av_bd_m:
            logging.info(f'av_by <- models result: {abs(l_av_m - l_av_bd_m)}')


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
            await db.execute(
                """UPDATE brands SET %(set_row)s = $brand_data WHERE [unique]=$brand""" % {"set_row": set_row},
                (brand_data[brand][index], brand,))
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
    cursor_av_m = await db.execute("""
            select brands.[unique], models.[unique] from brands 
            inner join models on brands.id = models.brand_id 
        """)
    av_bd_m = await cursor_av_m.fetchall()
    for brand in model_data:
        for model in model_data[brand]:
            if (brand, model) in av_bd_m:
                await db.execute(
                    """UPDATE models SET %(set_row)s = $model_data WHERE [unique]=$model""" % {"set_row": set_row},
                    (model_data[brand][model][index], model,))
    await db.commit()
    logging.info(f'{set_row} <- models is comitted')


async def delete_dublicates(db, table: str):
    """
    Удаляем дубликаты в таблице с уникальным id
    :param db: инструкция к БД
    :param table: имя таблицы
    :return: None
    """
    cursor = await db.execute("""SELECT * FROM %(table)s""" % {"table": table})
    rows = await cursor.fetchall()
    unique_list = []

    for row in rows:
        if row[1::] not in [i[1::] for i in unique_list]:
            unique_list.append(row)
        else:
            await db.execute("""DELETE FROM $table WHERE id=$row ORDER BY DATE""", (table, row[0],))
            logging.info(f'dublicate: {table}: {row}')
    await db.commit()


async def main(db: database()):
    """
    Выполняем сценарий по созданию и наполнению БД
    :return: None
    """
    b_m: dict = car_data()
    l_b_m = l_car_data(**b_m)
    async with db:
        if checking_null(**l_b_m):
            await create(db)
            await av_brands(db, b_m["av_b"], l_b_m["l_av_b"]),
            await av_models(db, b_m["av_m"], l_b_m["l_av_m"]),
            await add_brand(db, b_m["abw_b"], 'abw_by', 1),
            await add_brand(db, b_m["onliner_b"], 'onliner_by', 0),
            await add_brand(db, b_m["kufar_b"], 'kufar_by', 0),
            await add_model(db, b_m["abw_m"], 'abw_by', 2),
            await add_model(db, b_m["onliner_m"], 'onliner_by', 0),
            await add_model(db, b_m["kufar_m"], 'kufar_by', 0),
            await delete_dublicates(db, 'brands')
            await delete_dublicates(db, 'models')
        else:
            logging.warning('Присутствуют пустые словари в папке parse')
