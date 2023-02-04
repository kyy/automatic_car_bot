import asyncio
import numpy as np
from aiohttp import ClientSession
import requests
from multiprocessing import Pool
import nest_asyncio


nest_asyncio.apply()

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}

root = 'https://api.av.by/offer-types/cars/filters/main/init?'
url = 'https://api.av.by/offer-types/cars/filters/main/init?brands[0][brand]=6&brands[0][model]=1992&engine_type[0]=1'


def count_cars_av(url):
    r = requests.get(url, headers=headers).json()
    return int(r['count'])


def json_links_av_by(url):
    links_to_json = []
    r = requests.get(url, headers=headers).json()
    #page_count = r['pageCount']
    page_count = 5  # ограничиваем количество стрниц
    links_to_json.append(url)
    i = 1
    if page_count > 1:
        while page_count > 1:
            i += 1
            links_to_json.append(f'{url}&page={i}')
            page_count -= 1
    return links_to_json


def json_parse_av_by(json_data):
    car = []
    for i in range(len(json_data['adverts'])):
        r_t = json_data['adverts'][i]
        price = r_t['price']['usd']['amount']
        days = r_t['originalDaysOnSale']    # дни в продаже
        exchange = r_t['exchange']['label'].replace('Обмен ', '').replace(' обмен', '')
        city = r_t['shortLocationName']
        url = r_t['publicUrl']
        year = r_t['year']
        brand = r_t['properties'][0]['value']
        model = r_t['properties'][1]['value']
        try:
            vin = r_t['metadata']['vinInfo']['vin']
        except:
            vin = 'None'
        generation = motor = dimension = transmission = km = type = drive = color = None
        for j in range(len(json_data['adverts'][i]['properties'])):
            r_t = json_data['adverts'][i]['properties'][j]
            if r_t['name'] == 'mileage_km':
                km = r_t['value']
            if r_t['name'] == 'engine_endurance':
                dimension = r_t['value']
            if r_t['name'] == 'engine_capacity':
                dimension = r_t['value']
            if r_t['name'] == 'engine_type':
                motor = r_t['value'].replace('пропан-бутан', 'пр-бут')
            if r_t['name'] == 'transmission_type':
                transmission = r_t['value']
            if r_t['name'] == 'color':
                color = r_t['value']
            if r_t['name'] == 'drive_type':
                drive = r_t['value'].replace('привод', '')
            if r_t['name'] == 'body_type':
                type = r_t['value']
            if r_t['name'] == 'generation':
                generation = r_t['value']
        car.append([url, 'comment', f'{brand} {model} {generation}', price, motor, dimension, transmission, km, year,
                    type, drive, color, vin, exchange, days, city])
    return car


async def bound_fetch(semaphore, url, session, result):
    try:
        async with semaphore:
            await get_one(url, session, result)
    except Exception as e:
        print(e)
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one(url, session, result):
    async with session.get(url) as response:
        page_content = await response.json()   # Ожидаем ответа и блокируем таск.
        item = json_parse_av_by(page_content)      # Получаем информацию об машине и сохраняем в лист.
        result += item
        #await asyncio.sleep(0.1)


async def run(urls, result):
    tasks = []
    # Выбрал лок от балды. Можете поиграться.
    semaphore = asyncio.Semaphore(5)
    headers = {"User-Agent": "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"}
    # Опять же оставляем User-Agent, чтобы не получить ошибку от Metacritic
    async with ClientSession(headers=headers) as session:
        for url in urls:
            # Собираем таски и добавляем в лист для дальнейшего ожидания.
            task = asyncio.ensure_future(bound_fetch(semaphore, url, session, result))
            tasks.append(task)
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)


def parse_main(url, message, name):
    result = []
    # Запускаем наш парсер.
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(json_links_av_by(url), result))
    loop.run_until_complete(future)
    np.save(f'b_logic/buffer/{message}{name}.npy', result)
    print(result)
    return result


if __name__ == "__main__":
    pass
