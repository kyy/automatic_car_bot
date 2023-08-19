import asyncio
import numpy as np
from aiohttp import ClientSession
from .constant import HEADERS, API
from .parse_sites.abw_by import json_parse_abw, json_links_abw
from .parse_sites.av_by import json_parse_av, json_links_av
from .parse_sites.kufar_by import json_links_kufar, json_parse_kufar
from .parse_sites.onliner_by import json_parse_onliner, json_links_onliner
import nest_asyncio


nest_asyncio.apply()


def urls(json, work):

    av = json['av_json']
    abw = json['abw_json']
    onliner = json['onliner_json']
    kufar = json['kufar_json']

    cars = []

    if av:
        cars.extend([*json_links_av(av, work)])
    if abw:
        cars.extend([*json_links_abw(abw)])
    if onliner:
        cars.extend([*json_links_onliner(onliner, work)])
    if kufar:
        cars.extend([*json_links_kufar(kufar)])
    return cars


async def bound_fetch(semaphore, url, session, result, work):
    try:
        async with semaphore:
            await get_one(url, session, result, work)
    except Exception as e:
        print(e, '[cook_parse_cars.bound_fetch]')
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one(url, session, result, work):
    async with session.get(url) as response:
        page_content = await response.json()
        if url.split('/')[2] == API['AV']:
            item = json_parse_av(page_content, work)
        if url.split('/')[2] == API['ONLINER']:
            item = json_parse_onliner(page_content, work)
        if url.split('/')[2] == API['ABW']:
            item = json_parse_abw(page_content, work)
        if url.split('/')[2] == API['KUFAR']:
            item = json_parse_kufar(page_content, work)
        result += item


async def run(allurls, result, work):
    tasks = []
    semaphore = asyncio.Semaphore(20)
    async with ClientSession(headers=HEADERS) as session:
        if allurls:
            for url in allurls:
                task = asyncio.ensure_future(bound_fetch(semaphore, url, session, result, work))
                tasks.append(task)
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)
        await session.close()


async def parse_main(json, tel_id, name, work=False, send_car_job=None):
    """
    :param av: ссылка на json со всеми обявлениями
    :param abw: ссылка на json со всеми обявлениями
    :param onliner: ссылка на json со всеми обявлениями
    :param tel_id: id of telegram user
    :param name: id of filter or timestump
    :param work: True - задачи таска task_worker
    :param send_car_job: True - отправляемв в очередь задания на отправку обяъвлений
    :return: result список машин с параметрами [[],[]...]
    """
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        run(urls(json, work=work), result, work))
    loop.run_until_complete(future)
    if work is True:
        await send_car_job(tel_id, result)
    else:
        np.save(f'logic/buffer/{name}.npy', result)
    return result
