import asyncio
import logging

from logic.constant import LOGO
from logic.cook_parse_cars import parse_main as cars
from logic.cook_parse_prices import parse_main as prices
from logic.cook_pdf import do_pdf
from logic.database.config import database, backup_db
from logic.database.data_migrations import main as update
from logic.func import off_is_active
from logic.dublicate_find import check_dublicate, CacheCarData

from sites.sites_get_data import all_json, get_photos
from sites.sites_get_update import get_parse_brands_models

from arq.connections import RedisSettings
from arq import create_pool

from load_env import bot
from bot.keyboards import car_message_kb, delete_message_kb, car_price_message_kb

import os
from aiogram.types import FSInputFile

LOCAL_HOST = '127.0.0.1'
DOCKER_HOST = 'redis'

rs = RedisSettings(host=LOCAL_HOST, port=6379)


async def update_database(ctx) -> None:
    """Бекап БД, парсинг брендов моделей, бновление БД."""
    await backup_db()
    await get_parse_brands_models()
    await update(database())


async def reset_subs(ctx) -> None:
    """Сброс активных поисков до установленного кол-ва при окончании подписки"""
    await off_is_active()
    logging.info('RESET ACTIVE STATUS')


async def parse_cars(ctx, item, work) -> None:
    """Парсинг объявлений машин :param work:  Флаг True: отчет"""
    filt, tel_id, name = item[1][7:], item[0], item[2]
    json = await all_json(filt, work)
    await cars(json, tel_id, name, work, send_car_job)


async def parse_cars_job(ctx):
    """Создаем очередь парсинга обявлений"""
    redis = await create_pool(rs)
    async with database() as db:
        select_filters_cursor = await db.execute(
            "SELECT user.tel_id, udata.search_param, udata.id FROM udata "  # noqa  
            "INNER JOIN user on user.id = udata.user_id "
            "WHERE udata.is_active = 1 "
            "ORDER BY udata.id ")
        select_filters = await select_filters_cursor.fetchall()
        for item in select_filters:
            await asyncio.sleep(0.105)
            await redis.enqueue_job('parse_cars', item, True)


async def send_car(ctx, tel_id, car, ccd):
    """Отправка объявлений"""
    url, price, photo = car[0], car[1], car[2]
    photo = FSInputFile(LOGO) if photo == '' else photo
    message = f'{url}\n${price}'
    try:
        await bot.send_photo(tel_id, caption=message, photo=photo, reply_markup=car_message_kb(url))
        ccd.push([url.split('/')[-1]])
        logging.info(f"send car -> {tel_id} <- {url}")
    except Exception as e:
        logging.error(f"<work.send_car> <url> {url} <photo> {photo} {e}")


async def send_car_job(tel_id, result):
    """Создаем очередь отправки объявлений"""
    redis = await create_pool(rs)
    ccd = CacheCarData(tel_id, 50)

    for car in result:
        if not check_dublicate(url=car[0].split('/')[-1], ccd=ccd):
            await asyncio.sleep(0.205)
            await redis.enqueue_job('send_car', tel_id, car, ccd)


async def parse_price(ctx):
    """Парсинг цен"""
    await prices(send_new_price_job)


async def send_new_price(ctx, row, photo, url, current_price):
    """Отправляем объявление с новой ценой"""
    try:
        await bot.send_photo(row[0],
                             caption=f'Старая цена - {row[3]}$\n'
                                     f'Текущая цена - {current_price}$\n'
                                     f'Разница - {abs(row[3] - current_price)}$\n'
                                     f'{url}',
                             reply_markup=car_price_message_kb(url),
                             photo=photo,
                             parse_mode='HTML',
                             )
        logging.info(f'send new price -> {row[0]} <- {row[2]}')
    except Exception as e:
        logging.error(f'<cook_parse_prices.check_price> {e} {row[0]} {row[2]} id={row[1]}')
    async with database() as db:
        await db.execute("""UPDATE ucars SET price=$current_price WHERE url=$db_url""",
                         (current_price, row[2],))
        await db.commit()
        await asyncio.sleep(0.205)


async def send_new_price_job(result):
    """Создаем очередь объявлений с новой ценой"""
    redis = await create_pool(rs)
    async with database() as db:

        data_cursor = await db.execute("""
           SELECT user.tel_id, ucars.id, ucars.url, ucars.price FROM ucars
           INNER JOIN user on user.id = ucars.user_id
           ORDER BY ucars.url """)
        base_data = await data_cursor.fetchall()
        for car in result:

            current_price, url = car[0], car[1]

            image = await get_photos(url)

            photo = FSInputFile(LOGO) if image is False else image

            # tel_id=row[0] / db_id=row[1] / db_url=row[2] / db_price=row[3]
            for row in (row for row in base_data if row[2] == url and row[3] != current_price):
                await redis.enqueue_job('send_new_price', row, photo, url, current_price)


async def send_pdf(ctx, user_id, link_count, name_time_stump, decode_f_s, filter_name):
    """Отправка отчета"""
    await do_pdf(user_id, link_count, name_time_stump, decode_f_s, filter_name)
    bf = f'logic/buffer/{name_time_stump}'
    os.remove(f'{bf}.npy')
    if os.path.exists(f'{bf}.pdf'):
        file = FSInputFile(f'{bf}.pdf')
        await bot.send_document(chat_id=user_id,
                                document=file,
                                caption=decode_f_s,
                                reply_markup=delete_message_kb(),
                                parse_mode='HTML')
        os.remove(f'{bf}.pdf')
    else:
        logging.warning(f'{name_time_stump}.pdf не найден')
        await bot.send_message(user_id, 'отчет не удалось отправить')


async def send_pdf_job(*args):
    """Создаем очередь для отправки отчета"""
    redis = await create_pool(rs)
    await redis.enqueue_job('send_pdf', *args)
