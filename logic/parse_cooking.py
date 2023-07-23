import asyncio
import numpy as np
from aiohttp import ClientSession
import nest_asyncio
from arq import create_pool
from arq.connections import RedisSettings
from .parse_sites.av_by import json_links_av, bound_fetch_av
from .parse_sites.abw_by import json_links_abw, bound_fetch_abw
from .parse_sites.onliner_by import json_links_onliner, bound_fetch_onliner
from classes import bot


nest_asyncio.apply()


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
}


async def run(urls_av, urls_abw, urls_onliner, result, work):
    tasks = []
    semaphore = asyncio.Semaphore(10)
    async with ClientSession(headers=headers) as session:
        if urls_av:
            for url in urls_av:
                task = asyncio.ensure_future(bound_fetch_av(semaphore, url, session, result, work))
                tasks.append(task)
        if urls_abw:
            for url in urls_abw:
                task = asyncio.ensure_future(bound_fetch_abw(semaphore, url, session, result, work))
                tasks.append(task)
        if urls_onliner:
            for url in urls_onliner:
                task = asyncio.ensure_future(bound_fetch_onliner(semaphore, url, session, result, work))
                tasks.append(task)
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)


# async def send_car(tel_id, url):
#     try:
#         await bot.send_message(tel_id, url)
#     except Exception as e:
#         print(e)


async def parse_main(url_av, url_abw, url_onliner, message, name, work):
    """
    :param url_av: ссылка к json файлу
    :param url_abw: ссылка к json файлу
    :param url_onliner: ссылка к json файлу
    :param message: id of telegram user
    :param name: id of filter
    :param work: True - задачи таска task_worker
    :return: result список машин с параметрами [[],[]...]
    """
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(json_links_av(url_av),
                                       json_links_abw(url_abw),
                                       json_links_onliner(url_onliner),
                                       result, work,
                                       ))
    loop.run_until_complete(future)
    if work is True:
        redis = await create_pool(RedisSettings())
        for car in result:
            await redis.enqueue_job('send_car', message, car[0])
    else:
        np.save(f'logic/buffer/{name}.npy', result)
    return result
