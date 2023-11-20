import asyncio
import logging

from aiogram.types import FSInputFile
from lxml import etree
from aiohttp import ClientSession
from bot_config import bot
from keyboards import car_price_message_kb
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
                await db.execute(f"""DELETE FROM ucars WHERE id=$s""", (id_car,))
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
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)


async def check_price(result):
    async with database() as db:

        data_cursor = await db.execute("""
        SELECT user.tel_id, ucars.id, ucars.url, ucars.price FROM ucars
        INNER JOIN user on user.id = ucars.user_id
        ORDER BY ucars.url """)
        base_data = await data_cursor.fetchall()
        for car in result:

            current_price, url = car[0], car[1]

            image = await get_photos(url)

            photo = FSInputFile(LOGO) if image is False else image

            # tel_id=row[0] / db_id=row[1] / db_url=row[2] / db_price=row[3]
            for row in (row for row in base_data if row[2] == url and row[3] != current_price):

                db_price, db_url = row[3], row[2]

                if db_price != 0:
                    try:
                        await bot.send_photo(row[0],
                                             caption=
                                             f'Старая цена - {db_price}$\n'
                                             f'Текущая цена - {current_price}$\n'
                                             f'Разница - {abs(db_price - current_price)}$\n'
                                             f'{url}',
                                             reply_markup=car_price_message_kb(url),
                                             photo=photo,
                                             parse_mode='HTML',
                                             )
                    except Exception as e:
                        logging.error(f'<cook_parse_prices.check_price> {e}')

                await db.execute("""UPDATE ucars SET price=$current_price WHERE url=$db_url""",
                                 (current_price, db_url,))
        await db.commit()


async def parse_main(ctx):
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(await json_urls(), await html_urls(), result=result))
    loop.run_until_complete(future)
    await check_price(result)
    return result
