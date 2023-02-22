import asyncio
import requests
from datetime import datetime

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}


def count_cars_onliner(url):
    try:
        r = requests.get(url, headers=headers).json()
        return int(r['total'])
    except:
        return 0


def json_links_onliner(url):
    try:
        links_to_json = []
        r = requests.get(url, headers=headers).json()
        page_count = r['page']['last']
        links_to_json.append(url)
        i = 1
        if page_count > 3:  # - - - - - - ограничение вывода страниц
            page_count = 3  # - - - - - - ограничение вывода страниц
            while page_count > 1:
                i += 1
                links_to_json.append(f'{url}&page={i}')
                page_count -= 1
        return links_to_json
    except:
        return False


def json_parse_onliner(json_data):
    car = []
    for i in range(len(json_data['adverts'])):
        r_t = json_data['adverts'][i]
        brand_model_gen = r_t['title']
        price = r_t['price']['converted']['usd']['amount']
        dca = r_t['created_at'].split('T')[0].split('-')
        days = datetime.now() - datetime.date(dca[0], dca[1], dca[2])
        city = r_t['location']['city']
        url = r_t['html_url']
        vin = 'None'
        exchange = ''
        year = r_t['specs']['year']
        km = r_t['specs']['odometr']['value']
        dimension = r_t['specs']['engine']['capacity']
        motor = r_t['specs']['engine']['type'].replace('gasoline', 'бензин')
        transmission = r_t['specs']['transmission']
        color = r_t['specs']['color']
        drive = r_t['specs']['drivertrain']
        type = r_t['specs']['body_type']
        brand = r_t['manufacturer']['name']
        model = r_t['model']['name']
        generation = r_t['generation']['name']
        car.append([url, 'comment', f'{brand_model_gen}', price, motor, dimension, transmission, km, year,
                    type, drive, color, vin, exchange, days, city])
    print(car)
    return car


async def bound_fetch_onliner(semaphore, url, session, result):
    try:
        async with semaphore:
            await get_one_onliner(url, session, result)
    except Exception as e:
        print(e)
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one_onliner(url, session, result):
    async with session.get(url) as response:
        page_content = await response.json()   # Ожидаем ответа и блокируем таск.
        item = json_parse_onliner(page_content)      # Получаем информацию об машине и сохраняем в лист.
        result += item
        #await asyncio.sleep(0.1)


