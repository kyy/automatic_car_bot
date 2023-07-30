import asyncio
import numpy as np
from aiohttp import ClientSession
import nest_asyncio
from .constant import HEADERS
from .parse_sites.av_by import json_links_av, bound_fetch_av
from .parse_sites.abw_by import json_links_abw, bound_fetch_abw
from .parse_sites.onliner_by import json_links_onliner, bound_fetch_onliner


nest_asyncio.apply()


async def run(urls_av, urls_abw, urls_onliner, result, work):
    tasks = []
    semaphore = asyncio.Semaphore(20)
    async with ClientSession(headers=HEADERS) as session:
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
        await session.close()



async def parse_main(url_av, url_abw, url_onliner, message, name, work=False, send_car_job=None):
    """
    :param url_av: ссылка к json файлу
    :param url_abw: ссылка к json файлу
    :param url_onliner: ссылка к json файлу
    :param message: id of telegram user
    :param name: id of filter
    :param work: True - задачи таска task_worker
    :param send_car_job: True - отправляемв в очередь задания на отправку обяъвлений
    :return: result список машин с параметрами [[],[]...]
    """
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        run(
            json_links_av(url_av, work),
            json_links_abw(url_abw),
            json_links_onliner(url_onliner, work),
            result, work,
        )
    )
    loop.run_until_complete(future)
    if work is True:
        await send_car_job(message, result)
    else:
        np.save(f'logic/buffer/{name}.npy', result)
    return result
