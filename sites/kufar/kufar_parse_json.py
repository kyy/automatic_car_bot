import logging
from datetime import datetime
import requests
from lxml import etree

from logic.constant import WORK_PARSE_CARS_DELTA, HEADERS_JSON, ROOT, HEADERS
from logic.decorators import timed_lru_cache



@timed_lru_cache(300)
def count_cars_kufar(url):
    if url is None:
        return 0
    try:
        r = requests.get(url.replace("rendered-paginated?", "count?"), headers=HEADERS_JSON).json()
        return int(r["count"])
    except Exception as e:
        logging.error(f'<count_cars_kufar> {e}')
        return 0


@timed_lru_cache(300)
def json_links_kufar(url):
    if url == ROOT['KUFAR']:
        return False
    return [url, ] if url else False


def json_parse_kufar(json_data, work):
    car = []
    for i in range(len(json_data["ads"])):
        r_t = json_data["ads"][i]
        try:
            photo = r_t["images"][0]["path"]
            photo = f'https://rms.kufar.by/v1/gallery/{photo}'
        except:
            photo = ''
        published = r_t["list_time"]
        price = int(float(r_t["price_usd"]) / 100)
        url = r_t["ad_link"]
        days = (datetime.now().date() - datetime.strptime(published.split("T")[0], "%Y-%m-%d").date()).days
        motor = dimension = transmis = km = typec = drive = color = brand = model = year = exchange = city = vin = ""
        for j in range(len(r_t["ad_parameters"])):
            r_t = json_data["ads"][i]["ad_parameters"][j]
            if r_t["p"] == "area":
                city = r_t["vl"]
            elif r_t["p"] == "brand":
                brand = r_t["vl"]
            elif r_t["p"] == "cars_level_1":
                model = r_t["vl"]
            elif r_t["p"] == "full_vehicle_vin":
                vin = r_t["v"]
            elif r_t["p"] == "possible_exchange":
                exchange = r_t["vl"].casefold().replace("да", "возможен")
            elif r_t["p"] == "regdate":
                year = r_t["vl"]
            elif r_t["p"] == "mileage":
                km = r_t["v"] if r_t["vl"] == "" else r_t["vl"]
                km = str(km).replace("км", "")
            elif r_t["p"] == "cars_capacity":
                dimension = r_t["vl"].replace("л", "")
            elif r_t["p"] == "cars_engine":
                motor = r_t["vl"].casefold().replace("бензин (пропан-бутан)", "бензин (пр-бут)")
            elif r_t["p"] == "cars_gearbox":
                transmis = r_t["vl"].casefold().replace("автоматическая", "авотмат")
            elif r_t["p"] == "cars_autogearbox":
                transmis = r_t["vl"].casefold()
            elif r_t["p"] == "cars_color":
                color = r_t["vl"].casefold()
            elif r_t["p"] == "cars_drive":
                drive = r_t["vl"].casefold()
            elif r_t["p"] == "cars_type":
                typec = r_t["vl"].casefold()

        if work is True:
            fresh_minutes = datetime.now() - datetime.strptime(published[:-4], "%Y-%m-%dT%H:%M")
            fresh_minutes = fresh_minutes.total_seconds() / 60
            if fresh_minutes <= WORK_PARSE_CARS_DELTA * 60 + 180:
                car.append([str(url), str(price), str(photo)])
        else:
            car.append(
                [
                    str(url),
                    "comment",
                    f"{str(brand)} {str(model)}",
                    str(price),
                    str(motor),
                    str(dimension),
                    str(transmis),
                    str(km),
                    str(year),
                    str(typec),
                    str(drive),
                    str(color),
                    str(vin),
                    str(exchange),
                    str(days),
                    str(city),
                ]
            )
    return car


def get_car_html(id_car):
    url = f'{ROOT["KUFAR"]}vi/{id_car}'
    try:
        response = requests.get(url, HEADERS)
        page_content = response.text
        return etree.HTML(str(page_content))
    except Exception as e:
        logging.error(f'<kufar_by.kufar_json_by_id> {e}')
        return False


def kufar_research(id_car):
    dom = get_car_html(id_car)
    price = dom.xpath('//*[@data-name="additional-price"]')[0].text
    city = dom.xpath('//*[@data-name="ad_region_listing"]')[0].text


    # text = TEXT_DETAILS.format(
    #     url=url, price=price, brand=brand, model=model, generation=generation, year=year, motor=motor,
    #     dimension=dimension, color=color, typec=typec, status=status, vin=vin, vin_check=vin_check, city=city,
    #     descr=descr[:LEN_DESCRIPTION], days=days, transmission=transmission, drive=drive, km=km,
    # )
    return False, False