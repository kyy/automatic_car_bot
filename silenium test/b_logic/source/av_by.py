import asyncio
import requests


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}


def count_cars_av(url):
    r = requests.get(url, headers=headers).json()
    return int(r['count'])


def json_links_av(url):
    links_to_json = []
    r = requests.get(url, headers=headers).json()
    page_count = r['pageCount']
    links_to_json.append(url)
    i = 1
    if page_count > 5:  # - - - - - - ограничение вывода страниц
        page_count = 5  # - - - - - - ограничение вывода страниц
        while page_count > 1:
            i += 1
            links_to_json.append(f'{url}&page={i}')
            page_count -= 1
    return links_to_json


def json_parse_av(json_data):
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
        page_content = await response.json()   # Ожидаем ответа и блокируем таск.
        item = json_parse_av(page_content)      # Получаем информацию об машине и сохраняем в лист.
        result += item
        #await asyncio.sleep(0.1)



