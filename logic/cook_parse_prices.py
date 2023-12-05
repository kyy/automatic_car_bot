import asyncio
import logging
from aiogram.types import FSInputFile
from lxml import etree
from aiohttp import ClientSession

from load_env import bot
from bot.keyboards import car_price_message_kb

from sites.av.av_parse_json import json_parse_price_av
from sites.kufar.kufar_parse_json import html_parse_price_kufar
from sites.onliner.onliner_parse_json import json_parse_price_onliner
from sites.sites_fu import json_urls, html_urls
from sites.sites_get_data import get_photos

from .constant import HEADERS, API_DOMEN, ROOT_URL, LOGO
from logic.database.config import database


async def bound_fetch_json(semaphore, url, session, result):
    try:
        async with semaphore:
            await get_one_json(url, session, result)
    except Exception as e:
        logging.error(f'<cook_parse_cars.bound_fetch_json> {e}')
        await asyncio.sleep(1)


async def bound_fetch_html(semaphore, url, session, result):
    try:
        async with semaphore:
            await get_one_html(url, session, result)
    except Exception as e:
        logging.error(f'<cook_parse_cars.bound_fetch_html> {e}')
        await asyncio.sleep(1)


async def get_one_json(url, session, result):
    url, id_car = url[0], url[1]
    async with session.get(url) as response:
        if response.status == 404:
            async with database() as db:
                await db.execute("""DELETE FROM ucars WHERE id=$s""", (id_car,))
                await db.commit()
        else:
            page_content = await response.json()
            if url.split('/')[2] == API_DOMEN['AV']:
                item = json_parse_price_av(page_content)
            if url.split('/')[2] == API_DOMEN['ONLINER']:
                item = json_parse_price_onliner(page_content)
            result += item


async def get_one_html(url, session, result):
    url, id_car = url[0], url[1]
    async with session.get(url) as response:
        if response.status == 404:
            async with database() as db:
                await db.execute("""DELETE FROM ucars WHERE id=$s""", (id_car,))
                await db.commit()
        else:
            page_content = await response.text()
            page_content = etree.HTML(str(page_content))

            if url.split('/')[2] == ROOT_URL['KUFAR'].split('/')[2]:
                item = html_parse_price_kufar(page_content, url)

            result += item


async def run(json, html, result):
    tasks = []

    semaphore = asyncio.Semaphore(20)

    async with ClientSession(headers=HEADERS) as session:
        if json:
            for url in json:
                task = asyncio.ensure_future(bound_fetch_json(semaphore, url, session, result))
                tasks.append(task)
        if html:
            for url in html:
                task = asyncio.ensure_future(bound_fetch_html(semaphore, url, session, result))
                tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


async def parse_main(check_price=None):
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(await json_urls(), await html_urls(), result=result))
    loop.run_until_complete(future)
    await check_price(result)
    return result
