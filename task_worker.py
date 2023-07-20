import asyncio
from arq import create_pool, cron
from arq.connections import RedisSettings
from b_logic.database.config import database
from b_logic.database.data_migrations import main as update, lenn
from b_logic.database.main_parse import main_parse
from b_logic.get_url_cooking import all_get_url
from b_logic.parse_cooking import parse_main, send_car as send_car_from_parse


async def parse(ctx, car, message, name, work):
    av_link_json, abw_link_json, onliner_link_json = await all_get_url(car, work)
    await parse_main(av_link_json, abw_link_json, onliner_link_json, message, name, work)


async def send_car(ctx, tel_id, url):
    await send_car_from_parse(tel_id, url)


async def base(ctx):
    if main_parse(lenn):
        asyncio.run(update(database()))


async def collect_data(ctx):
    redis = await create_pool(RedisSettings())
    async with database() as db:
        select_filters_cursor = await db.execute(f"""
        SELECT user.tel_id, udata.search_param, udata.id FROM udata
        INNER JOIN user on user.id = udata.user_id
        WHERE udata.is_active=1 
        ORDER BY user.tel_id ASC 
        """)
        select_filters = await select_filters_cursor.fetchall()
        for item in select_filters:
            await redis.enqueue_job('parse', item[1][7:], item[0], item[2], True)


class WorkerSettings:
    functions = [parse, send_car]
    cron_jobs = [
        cron(collect_data, hour={i for i in range(1, 24)}, minute={00, 30}, run_at_startup=False,),   # парсинг новых объявлений
        cron(base, hour={00}, minute={15}, max_tries=3, run_at_startup=True),  # обновление БД
    ]

