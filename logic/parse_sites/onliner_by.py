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
    except requests.exceptions.RequestException:
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
    except requests.exceptions.RequestException:
        return False


def json_parse_onliner(json_data, work):
    car = []
    for i in range(len(json_data['adverts'])):
        r_t = json_data['adverts'][i]
        published = r_t['created_at']
        fresh_minutes = (datetime.now().timestamp() - datetime.strptime(published[:-9],
                                                                        "%Y-%m-%dT%H:%M").timestamp()) / 60
        url = r_t['html_url']
        if work is False:
            brand_model_gen = r_t['title']
            price = r_t['price']['converted']['USD']['amount'].split('.')[0]
            days = (datetime.now().date() - datetime.strptime(r_t['created_at'].split('T')[0], '%Y-%m-%d').date()).days
            city = r_t['location']['city']['name']

            vin = ''
            exchange = ''
            year = r_t['specs']['year']
            km = r_t['specs']['odometer']['value']
            dimension = r_t['specs']['engine']['capacity']
            motor = r_t['specs']['engine']['type'].replace('gasoline', 'бензин').replace('diesel', 'дизель')
            transmis = r_t['specs']['transmission'].replace('mechanical ', 'механика').replace('automatic', 'автомат')
            color = r_t['specs']['color']
            drive = r_t['specs']['drivetrain']
            typec = r_t['specs']['body_type']
            # brand = r_t['manufacturer']['name']
            # model = r_t['model']['name']
            # generation = r_t['generation']['name']
            car.append([
                str(url), 'comment', f'{str(brand_model_gen)}', str(price), str(motor), str(dimension),
                str(transmis), str(km), str(year), str(typec), str(drive), str(color), str(vin),
                str(exchange), str(days), str(city)
            ])
        if work is True and fresh_minutes < 29:
            car.append([str(url)])
    return car


async def bound_fetch_onliner(semaphore, url, session, result, work):
    try:
        async with semaphore:
            await get_one_onliner(url, session, result, work)
    except Exception as e:
        print(e)
        print('bound_fetch_onliner error')
        # Блокируем все таски на <> секунд в случае ошибки 429.
        await asyncio.sleep(1)


async def get_one_onliner(url, session, result, work):
    async with session.get(url) as response:
        page_content = await response.json()         # Ожидаем ответа и блокируем таск.
        item = json_parse_onliner(page_content, work)      # Получаем информацию об машине и сохраняем в лист.
        result += item
