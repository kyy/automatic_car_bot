import asyncio
import logging

import nest_asyncio
from aiohttp import ClientSession, TCPConnector
from aiolimiter import AsyncLimiter

import numpy as np

from logic.constant import HEADERS, API_DOMEN

from sites.abw.abw_parse_json import json_parse_abw
from sites.av.av_parse_json import json_parse_av
from sites.kufar.kufar_parse_json import json_parse_kufar
from sites.onliner.onliner_parse_json import json_parse_onliner
from sites.sites_get_data import urls_json

nest_asyncio.apply()

MAX_CONCURRENT = 4

rate_limit = AsyncLimiter(4, 1.0)


async def bound_fetch_json(semaphore, url, session, result, work):
    try:
        async with semaphore:
            async with rate_limit:
                await get_one_json(url, session, result, work)
    except Exception as e:
        logging.error(f'<cook_parse_cars.bound_fetch_json> {e}')
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one_json(url, session, result, work):
    item = None
    response = await session.get(url)

    page_content = await response.json()

    if url.split("/")[2] == API_DOMEN["AV"]:
        item = json_parse_av(page_content, work)

    elif url.split("/")[2] == API_DOMEN["ONLINER"]:
        item = json_parse_onliner(page_content, work)

    elif url.split("/")[2] == API_DOMEN["KUFAR"]:
        item = json_parse_kufar(page_content, work)

    elif url.split('/')[2] == API_DOMEN['ABW']:
        item = json_parse_abw(page_content, work)

    result += item


async def run(json, result, work):
    tasks = []

    semaphore = asyncio.Semaphore(20)
    connector = TCPConnector(limit=MAX_CONCURRENT)
    async with ClientSession(headers=HEADERS, connector=connector) as session:

        if json:
            for url in json:
                task = asyncio.ensure_future(bound_fetch_json(semaphore, url, session, result, work))
                tasks.append(task)

        await asyncio.gather(*tasks)


async def parse_main(json, tel_id, name, work=False, send_car_job=None):
    """
    :param json: dict with to json pages links
    :param tel_id: id of telegram user
    :param name: id of filter or timestump
    :param work: True - задачи таска task_worker
    :param send_car_job: True - отправляемв в очередь задания на отправку обяъвлений
    :return: result список машин с параметрами [[],[]...]
    """
    result = []

    json_links = await urls_json(json, work)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(json_links, result, work))
    loop.run_until_complete(future)
    if work is True:
        await send_car_job(tel_id, result)
    else:
        np.save(f"logic/buffer/{name}.npy", result)
    return result
