import asyncio
from httpx import AsyncClient
from arq import create_pool
from arq.connections import RedisSettings

from b_logic.get_url_cooking import all_get_url
from b_logic.parse_cooking import parse_main


async def parse(ctx, car):
    av_link_json, abw_link_json, onliner_link_json = await all_get_url(car)
    result = parse_main(av_link_json, abw_link_json, onliner_link_json, message='test', name='01')
    return print(result)


async def startup(ctx):
    ctx['session'] = AsyncClient()

async def shutdown(ctx):
    await ctx['session'].aclose()

async def main():
    redis = await create_pool(RedisSettings())
    for car in ('BMW+X3+d+a+1996+2020+?+?+?+?', 'BMW+X5+d+a+1996+2012+?+?+?+?'):
        await redis.enqueue_job('parse', car)

# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker
class WorkerSettings:
    functions = [parse]
    on_startup = startup
    on_shutdown = shutdown

if __name__ == '__main__':
    asyncio.run(main())
