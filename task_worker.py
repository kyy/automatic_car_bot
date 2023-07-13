import asyncio
import aiosqlite
from httpx import AsyncClient
from arq import create_pool
from arq.connections import RedisSettings
from b_logic.database.config import db_name
from b_logic.get_url_cooking import all_get_url
from b_logic.parse_cooking import parse_main


async def parse(ctx, car, message, name, work):
    av_link_json, abw_link_json, onliner_link_json = await all_get_url(car)
    parse_main(av_link_json, abw_link_json, onliner_link_json, message, name, work)


async def startup(ctx):
    ctx['session'] = AsyncClient()

async def shutdown(ctx):
    await ctx['session'].aclose()

async def main():
    redis = await create_pool(RedisSettings())
    async with aiosqlite.connect(db_name) as db:
        select_cursor = await db.execute(f"""
        SELECT user.tel_id, udata.search_param, udata.id FROM udata
        INNER JOIN user on user.id = udata.user_id
        WHERE udata.is_active=1 
        ORDER BY user.tel_id ASC 
        """)
        select = await select_cursor.fetchall()
    for item in select:
        await redis.enqueue_job('parse', item[1][7:], item[0], item[2], True)

# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker
class WorkerSettings:
    functions = [parse]
    on_startup = startup
    on_shutdown = shutdown

if __name__ == '__main__':
    asyncio.run(main())
