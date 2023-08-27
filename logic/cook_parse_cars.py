import asyncio
import nest_asyncio
import numpy as np
from lxml import etree
from aiohttp import ClientSession

from .constant import HEADERS, API, ROOT

from .parse_sites.abw_by import json_parse_abw, html_links_abw, html_parse_abw
from .parse_sites.av_by import json_parse_av, json_links_av
from .parse_sites.kufar_by import json_links_kufar, json_parse_kufar
from .parse_sites.onliner_by import json_parse_onliner, json_links_onliner

nest_asyncio.apply()


def urls_json(json, work):
    av = json["av_json"]
    onliner = json["onliner_json"]
    kufar = json["kufar_json"]

    cars = []

    if av:
        cars.extend([*json_links_av(av, work)])
    if onliner:
        cars.extend([*json_links_onliner(onliner, work)])
    if kufar:
        cars.extend([*json_links_kufar(kufar)])
    return cars


def urls_html(json, html, work):
    abw_h = html["abw_link"]
    abw_j = json["abw_json"]

    cars = []

    if abw_h and abw_j:
        cars.extend([*html_links_abw(abw_j, abw_h, work)])
    return cars


async def bound_fetch_json(semaphore, url, session, result, work):
    try:
        async with semaphore:
            await get_one_json(url, session, result, work)
    except Exception as e:
        print(e, "[cook_parse_cars.bound_fetch_json]")
        print(url)
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one_json(url, session, result, work):
    async with session.get(url) as response:
        page_content = await response.json()
        if url.split("/")[2] == API["AV"]:
            item = json_parse_av(page_content, work)
        elif url.split("/")[2] == API["ONLINER"]:
            item = json_parse_abw(page_content, work)
        elif url.split("/")[2] == API["KUFAR"]:
            item = json_parse_kufar(page_content, work)
        result += item


async def bound_fetch_html(semaphore, url, session, result, work):
    try:
        async with semaphore:
            await get_one_html(url, session, result, work)
    except Exception as e:
        print(e, "[cook_parse_cars.bound_fetch_html]")
        print(url)
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one_html(url, session, result, work):
    async with session.get(url) as response:
        if response.status == 404:
            pass
        else:
            page_content = await response.text()
            page_content = etree.HTML(str(page_content))
            if url.split('/')[2] == ROOT['ABW'].split('/')[2]:
                item = html_parse_abw(page_content, url, work)

            result += item


async def run(json, html, result, work):
    tasks = []
    semaphore = asyncio.Semaphore(20)
    async with ClientSession(headers=HEADERS) as session:
        if json:
            for url in json:
                task = asyncio.ensure_future(bound_fetch_json(semaphore, url, session, result, work))
                tasks.append(task)
        if html:
            for url in html:
                task = asyncio.ensure_future(bound_fetch_html(semaphore, url, session, result, work))
                tasks.append(task)
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)
        await session.close()


async def parse_main(json, html, tel_id, name, work=False, send_car_job=None):
    """
    :param json: dict with to json pages links
    :param html: dict with to html pages links
    :param tel_id: id of telegram user
    :param name: id of filter or timestump
    :param work: True - задачи таска task_worker
    :param send_car_job: True - отправляемв в очередь задания на отправку обяъвлений
    :return: result список машин с параметрами [[],[]...]
    """
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(urls_json(json, work=work), urls_html(json, html, work=work), result, work))
    loop.run_until_complete(future)
    if work is True:
        await send_car_job(tel_id, result)
    else:
        np.save(f"logic/buffer/{name}.npy", result)
    return result
