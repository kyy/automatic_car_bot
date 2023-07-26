import asyncio
from arq import create_pool, cron
from arq.connections import RedisSettings
from classes import bot
from logic.database.config import database
from logic.database.data_migrations import main as update, lenn
from logic.database.main_parse import main_parse
from logic.get_url_cooking import all_get_url
from logic.parse_cooking import parse_main


async def parse(ctx, car, message, name, work):
    av_link_json, abw_link_json, onliner_link_json = await all_get_url(car, work)
    await parse_main(av_link_json, abw_link_json, onliner_link_json, message, name, work, send_car_job)


async def send_car(ctx, tel_id, url):
    await asyncio.sleep(0.5)
    await bot.send_message(tel_id, url)


async def update_database(ctx):
    if main_parse(lenn):
        asyncio.run(update(database()))


async def collect_data_job(ctx):
    redis = await create_pool(RedisSettings())
    async with database() as db:
        select_filters_cursor = await db.execute(f"""
        SELECT user.tel_id, udata.search_param, udata.id FROM udata
        INNER JOIN user on user.id = udata.user_id
        WHERE udata.is_active=1 
        ORDER BY udata.id """)
        select_filters = await select_filters_cursor.fetchall()
        for item in select_filters:
            await redis.enqueue_job('parse', item[1][7:], item[0], item[2], True)


async def send_car_job(message, result):
    redis = await create_pool(RedisSettings())
    for car in result:
        await redis.enqueue_job('send_car', message, car[0])


class Work:
    functions = [parse, send_car]
    cron_jobs = [
        cron(collect_data_job,
             hour={i for i in range(1, 24)},
             minute={00, 30},
             run_at_startup=True, ),   # парсинг новых объявлений
        cron(update_database,
             hour={00}, minute={15},
             max_tries=3,
             run_at_startup=False),  # обновление БД
    ]
