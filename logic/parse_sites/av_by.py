import asyncio
import requests
from datetime import datetime
from logic.constant import WORK_PARSE_DELTA, REPORT_PARSE_LIMIT_PAGES
from logic.decorators import timed_lru_cache


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}


def count_cars_av(url):
    try:
        r = requests.get(url, headers=headers).json()
        return int(r['count'])
    except requests.exceptions.RequestException:
        return 0


@timed_lru_cache(300)
def json_links_av(url, work):
    try:
        links_to_json = []
        r = requests.get(url, headers=headers).json()
        page_count = r['pageCount']
        if work is False:
            if page_count >= REPORT_PARSE_LIMIT_PAGES:  # - - - - - - ограничение вывода страниц
                page_count = REPORT_PARSE_LIMIT_PAGES   # - - - - - - для отчета
        links_to_json.append(url)
        i = 1
        while page_count > 1:
            i += 1
            links_to_json.append(f'{url}&page={i}')
            page_count -= 1
        return links_to_json
    except requests.exceptions.RequestException:
        return False


async def bound_fetch_av(semaphore, url, session, result, work):
    try:
        async with semaphore:
            await get_one(url, session, result, work)
    except Exception as e:
        print(e)
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one(url, session, result, work):
    async with session.get(url) as response:
        page_content = await response.json()   # Ожидаем ответа и блокируем таск.
        item = json_parse_av(page_content, work)      # Получаем информацию об машине и сохраняем в лист.
        result += item


def json_parse_av(json_data, work):
    car = []
    for i in range(len(json_data['adverts'])):
        r_t = json_data['adverts'][i]
        published = r_t['publishedAt']
        price = r_t['price']['usd']['amount']
        url = r_t['publicUrl']
        if work is False:
            # try:
            #     comments = r_t['description']
            # except:
            #     comments = ''
            days = r_t['originalDaysOnSale']    # дни в продаже
            exchange = r_t['exchange']['label'].replace('Обмен ', '').replace(' обмен', '')
            city = r_t['shortLocationName']
            year = r_t['year']
            brand = r_t['properties'][0]['value']
            model = r_t['properties'][1]['value']
            try:
                vin = r_t['metadata']['vinInfo']['vin']
            except:
                vin = ''
            generation = motor = dimension = transmission = km = typec = drive = color = ''
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
                    typec = r_t['value']
                if r_t['name'] == 'generation':
                    generation = r_t['value']
            car.append([
                str(url), str('comments'), f'{str(brand)} {str(model)} {str(generation)}', str(price),
                str(motor), str(dimension), str(transmission), str(km), str(year), str(typec),
                str(drive), str(color), str(vin), str(exchange), str(days), str(city)])
        else:
            fresh_minutes = datetime.now() - datetime.strptime(published[:-8], "%Y-%m-%dT%H:%M")
            fresh_minutes = fresh_minutes.total_seconds() / 60
            if fresh_minutes <= WORK_PARSE_DELTA * 60 + 180:
                car.append([str(url), str(price)])
    return car
