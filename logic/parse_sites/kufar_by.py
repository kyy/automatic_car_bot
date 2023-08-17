import requests
from datetime import datetime
from logic.constant import WORK_PARSE_CARS_DELTA, REPORT_PARSE_LIMIT_PAGES, HEADERS_JSON
from logic.decorators import timed_lru_cache


def count_cars_kufar(url):
    if url is None:
        return 0
    try:
        r = requests.get(url, headers=HEADERS_JSON).json()
        return int(r['total'])
    except Exception as e:
        print(e)
        return 0


@timed_lru_cache(300)
def json_links_kufar(url):
    return [url, ] if url else False


def json_parse_kufar(json_data, work):
    car = []
    for i in range(len(json_data['ads'])):
        r_t = json_data['ads'][i]
        published = r_t['list_time']
        price = r_t['paid_services']['price_usd']
        url = r_t['ad_link']
        brand = r_t['ad_parameters'][2]['vl']
        model = r_t['ad_parameters'][3]['vl']
        generation = ''
        days = (datetime.now().date() - datetime.strptime(r_t['created_at'].split('T')[0], '%Y-%m-%d').date()).days
        city = r_t['ad_parameters'][14]['vl']
        vin = ''
        exchange = ''
        year = r_t['ad_parameters'][4]['vl']
        km = r_t['specs']['odometer']['value']
        dimension = r_t['ad_parameters'][7]['vl']
        motor = r_t['ad_parameters'][6]['vl']
        transmis = r_t['ad_parameters'][8]['vl']
        color = r_t['ad_parameters'][11]['vl']
        drive = r_t['ad_parameters'][10]['vl']
        typec = r_t['ad_parameters'][9]['vl']

        if work is True:
            fresh_minutes = datetime.now() - datetime.strptime(published[:-9], "%Y-%m-%dT%H:%M")
            fresh_minutes = fresh_minutes.total_seconds() / 60
            if fresh_minutes <= WORK_PARSE_CARS_DELTA * 60:
                car.append([str(url), str(price)])
        else:
            car.append([
                str(url), 'comment', '{str(brand_model_gen)}', str(price), str(motor), str(dimension),
                str(transmis), str(km), str(year), str(typec), str(drive), str(color), str(vin),
                str(exchange), str(days), str(city)
            ])
    return car


# -------------follow-price
def car_json_by_id(id_car):
    url = f'https://ab.kufar.by/sdapi/ab.api/vehicles/{id_car}'
    try:
        r = requests.get(url, headers=HEADERS_JSON).json()
        return int(r['price']['converted']['USD']['amount'][:-3])
    except requests.exceptions.RequestException:
        return False
