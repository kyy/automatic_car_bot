import asyncio
from aiohttp import ClientSession

from classes import bot
from keyboards import delete_message_kb
from .constant import HEADERS, ONLINER_API, AV_API
from logic.database.config import database


async def json_links():
    async with database() as db:
        av_urls_cursor = await db.execute(
            f"""
            SELECT url FROM ucars 
            WHERE LOWER(url) LIKE 'https://cars.av.by/%' AND is_active = 1""")
        av_urls = await av_urls_cursor.fetchall()
        av_urls = [f"https://api.av.by/offers/{i[0].split('/')[-1]}" for i in av_urls]
        onliner_urls_cursor = await db.execute(
            f"""
            SELECT url FROM ucars
            WHERE LOWER(url) LIKE 'https://ab.onliner.by/%' AND is_active = 1""")
        onliner_urls = await onliner_urls_cursor.fetchall()
        onliner_urls = [f"https://ab.onliner.by/sdapi/ab.api/vehicles/{i[0].split('/')[-1]}" for i in onliner_urls]
        return [*av_urls, *onliner_urls]


async def bound_fetch_av(semaphore, url, session, result):
    try:
        async with semaphore:
            await get_one(url, session, result)
    except Exception as e:
        print(e)
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one(url, session, result):
    async with session.get(url) as response:
        page_content = await response.json()
        if url.split('/')[2] == AV_API:
            item = json_parse_av(page_content)
        if url.split('/')[2] == ONLINER_API:
            item = json_parse_onliner(page_content)
        result += item


def json_parse_av(json):
    return [[int(json['price']['usd']['amount']), str(json['publicUrl'])]]


def json_parse_onliner(json):
    return [[int(json['price']['converted']['USD']['amount'][:-3]), str(json['html_url'])]]


async def run(urls, result):
    tasks = []
    semaphore = asyncio.Semaphore(20)
    async with ClientSession(headers=HEADERS) as session:
        if urls:
            for url in urls:
                task = asyncio.ensure_future(bound_fetch_av(semaphore, url, session, result))
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
    future = asyncio.ensure_future(run(await json_links(), result))
    loop.run_until_complete(future)
    await check_price(result)
    return result

