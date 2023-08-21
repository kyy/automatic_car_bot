import asyncio
from lxml import etree
from aiohttp import ClientSession
from classes import bot
from keyboards import delete_message_kb
from .constant import HEADERS, API, ROOT
from logic.database.config import database


async def json_urls():
    async with database() as db:
        av_urls_cursor = await db.execute(
            f"""
            SELECT url, id FROM ucars 
            WHERE LOWER(url) LIKE 'https://cars.av.by/%' AND is_active = 1""")
        av_urls = await av_urls_cursor.fetchall()
        av_urls = [(f"https://api.av.by/offers/{i[0].split('/')[-1]}", i[1]) for i in av_urls]
        onliner_urls_cursor = await db.execute(
            f"""
            SELECT url, id FROM ucars
            WHERE LOWER(url) LIKE 'https://ab.onliner.by/%' AND is_active = 1""")
        onliner_urls = await onliner_urls_cursor.fetchall()
        onliner_urls = [(f"https://ab.onliner.by/sdapi/ab.api/vehicles/{i[0].split('/')[-1]}", i[1]) for i in onliner_urls]
        return [*av_urls, *onliner_urls]


async def html_urls():
    async with database() as db:
        kufar_abw_urls_cursor = await db.execute(
            f"""
            SELECT url, id FROM ucars
            WHERE (LOWER(url) LIKE 'https://auto.kufar.by/vi/%' OR LOWER(url) LIKE 'https://abw.by/cars/detail/%')
            AND is_active = 1""")
        kufar_abw_urls = await kufar_abw_urls_cursor.fetchall()
        kufar_abw_urls = [(i[0], i[1]) for i in kufar_abw_urls]
        return [*kufar_abw_urls]


async def bound_fetch_json(semaphore, url, session, result):
    # try:
        async with semaphore:
            await get_one_json(url, session, result)
    # except Exception as e:
    #     print(e, '[cook_parse_prices.bound_fetch_json]')
    #     await asyncio.sleep(1)


async def bound_fetch_html(semaphore, url, session, result):
    # try:
        async with semaphore:
            await get_one_html(url, session, result)
    # except Exception as e:
    #     print(e, '[cook_parse_prices.bound_fetch_html]')
    #     await asyncio.sleep(1)


async def get_one_json(url, session, result):
    url, id_car = url[0], url[1]
    async with session.get(url) as response:
        if response.status == 404:
            async with database() as db:
                await db.execute(f"""DELETE FROM ucars WHERE id={id_car}""")
                await db.commit()
        else:
            page_content = await response.json()
            if url.split('/')[2] == API['AV']:
                item = json_parse_av(page_content)
            if url.split('/')[2] == API['ONLINER']:
                item = json_parse_onliner(page_content)
            result += item


async def get_one_html(url, session, result):
    url, id_car = url[0], url[1]
    async with session.get(url) as response:
        if response.status == 404:
            async with database() as db:
                await db.execute(f"""DELETE FROM ucars WHERE id={id_car}""")
                await db.commit()
        else:
            page_content = await response.text()
            page_content = etree.HTML(str(page_content))
            if url.split('/')[2] == ROOT['ABW'].split('/')[2]:
                item = html_parse_abw(page_content, url)
            if url.split('/')[2] == ROOT['KUFAR'].split('/')[2]:
                item = html_parse_kufar(page_content, url)
            result += item


def json_parse_av(json):
    return [[int(json['price']['usd']['amount']), str(json['publicUrl'])]]


def json_parse_onliner(json):
    return [[int(json['price']['converted']['USD']['amount'][:-3]), str(json['html_url'])]]


def html_parse_abw(dom, url):
    price = dom.xpath('//*[@class="price-usd"]')[0].text
    price = price.replace(' ', '').replace('USD', '')
    return [[int(price), url]]


def html_parse_kufar(dom, url):
    price = dom.xpath('//*[@data-name="additional-price"]')[0].text
    price = price.replace(' ', '').replace('$*', '')
    return [[int(price), url]]


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
        await session.close()


async def check_price(result):
    async with database() as db:
        data_cursor = await db.execute(f"""
        SELECT user.tel_id, ucars.id, ucars.url, ucars.price FROM ucars
        INNER JOIN user on user.id = ucars.user_id
        ORDER BY ucars.url """)
        base_data = await data_cursor.fetchall()
        for car in result:
            for row in (row for row in base_data if row[2] == car[1] and row[3] != car[0]):
                print(row)
                if row[3] != 0:
                    await bot.send_message(row[0],
                                           f'Старая цена - {row[3]}$\n'
                                           f'Текущая цена - {car[0]}$\n'
                                           f'Разница - {abs(row[3] - car[0])}$\n'
                                           f'{car[1]}',
                                           reply_markup=delete_message_kb(),
                                           )
                await db.execute(f"""UPDATE ucars SET price='{car[0]}' WHERE url='{row[2]}'""")
        await db.commit()


async def parse_main(ctx):
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(await json_urls(), await html_urls(), result=result))
    loop.run_until_complete(future)
    await check_price(result)
    return result
