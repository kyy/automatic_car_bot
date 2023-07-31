import asyncio
import os
from aiogram.types import FSInputFile
from arq import create_pool, cron
from arq.connections import RedisSettings
from classes import bot
from keyboards import car_message_kb
from logic.constant import WORK_PARSE_DELTA
from logic.database.config import database
from logic.database.data_migrations import main as update, lenn
from logic.database.main_parse import main_parse as up
from logic.cook_url import all_get_url
from logic.cook_parse_cars import parse_main as cars
from logic.cook_pdf import do_pdf
from logic.cook_parse_prices import parse_main as prices


async def update_database(ctx):
    if up(lenn):
        asyncio.run(update(database()))


async def parse_cars(ctx, car, message, name, work):
    av_link_json, abw_link_json, onliner_link_json = await all_get_url(car, work)
    await cars(av_link_json, abw_link_json, onliner_link_json, message, name, work, send_car_job)


async def parse_cars_job(ctx):
    redis = await create_pool(RedisSettings())
    async with database() as db:
        select_filters_cursor = await db.execute(f"""
        SELECT user.tel_id, udata.search_param, udata.id FROM udata
        INNER JOIN user on user.id = udata.user_id
        WHERE udata.is_active = 1 
        ORDER BY udata.id """)
        select_filters = await select_filters_cursor.fetchall()
        for item in select_filters:
            await redis.enqueue_job('parse_cars', item[1][7:], item[0], item[2], True)


async def send_car(ctx, tel_id, url):
    await asyncio.sleep(0.5)
    await bot.send_message(tel_id, url, reply_markup=car_message_kb())


async def send_car_job(message, result):
    redis = await create_pool(RedisSettings())
    for car in result:
        await redis.enqueue_job('send_car', message, f'{car[0]}\n${car[1]}')


async def send_pdf(ctx, user_id, link_count, name_time_stump, decode_filter_short, filter_name):
    await do_pdf(user_id, link_count, name_time_stump, decode_filter_short, filter_name)
    bf = f'logic/buffer/{name_time_stump}'
    os.remove(f'{bf}.npy')
    if os.path.exists(f'{bf}.pdf'):
        file = FSInputFile(f'{bf}.pdf')
        await bot.send_document(user_id, document=file)
        os.remove(f'{bf}.pdf')
    else:
        print(f'{name_time_stump}.pdf не найден')
        await bot.send_message(user_id, 'отчет не удалось отправить')


async def send_pdf_job(*args):
    redis = await create_pool(RedisSettings())
    await redis.enqueue_job('send_pdf', *args)


async def parse_prices(ctx):
    await prices(check_price_job)


async def check_price(ctx, car):
    print(car)


async def check_price_job(result):
    redis = await create_pool(RedisSettings())
    for car in result:
        await redis.enqueue_job('check_price', car)


class Work:
    functions = [parse_cars, send_car, send_pdf, check_price]
    cron_jobs = [
        cron(parse_cars_job,
             hour={i for i in range(1, 24, WORK_PARSE_DELTA)},
             minute={00},
             run_at_startup=True),   # парсинг новых объявлений
        cron(update_database,
             hour={00},
             minute={15},
             max_tries=3,
             run_at_startup=False),  # обновление БД
        cron(parse_prices,
             hour={00},
             minute={15},
             run_at_startup=True),  # проверка цен
    ]
