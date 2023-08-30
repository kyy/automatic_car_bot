from datetime import datetime

import requests

from logic.constant import WORK_PARSE_CARS_DELTA, REPORT_PARSE_LIMIT_PAGES, HEADERS_JSON, PARSE_LIMIT_PAGES, ROOT
from logic.decorators import timed_lru_cache, timeit


@timed_lru_cache(300)
def count_cars_av(url):
    try:
        r = requests.get(url, headers=HEADERS_JSON).json()
        return int(r["count"])
    except Exception as e:
        print(e, ["logic.parse_sites.av_by.count_cars_av"])
        return 0


@timed_lru_cache(300)
def json_links_av(url, work):
    try:
        links_to_json = []
        r = requests.get(url, headers=HEADERS_JSON).json()
        page_count = r["pageCount"]
        limit_page = PARSE_LIMIT_PAGES if work is True else REPORT_PARSE_LIMIT_PAGES
        if page_count >= limit_page:  # - - - - - - ограничение вывода страниц
            page_count = limit_page  # - - - - - - для отчета
        links_to_json.append(url)
        i = 1
        while page_count > 1:
            i += 1
            links_to_json.append(f"{url}&page={i}")
            page_count -= 1
        return links_to_json
    except Exception as e:
        print(e)
        return False


def json_parse_av(json_data, work):
    car = []
    for i in range(len(json_data["adverts"])):
        r_t = json_data["adverts"][i]
        published = r_t["publishedAt"]
        price = r_t["price"]["usd"]["amount"]
        url = r_t["publicUrl"]

        # try:
        #     comments = r_t['description']
        # except:
        #     comments = ''
        days = r_t["originalDaysOnSale"]  # дни в продаже
        exchange = r_t["exchange"]["label"].casefold().replace("Обмен ", "").replace(" обмен", "")
        city = r_t["shortLocationName"]
        year = r_t["year"]
        brand = r_t["properties"][0]["value"]
        model = r_t["properties"][1]["value"]
        try:
            vin = r_t["metadata"]["vinInfo"]["vin"]
        except:
            vin = ""
        generation = motor = dimension = transmission = km = typec = drive = color = ""
        for j in range(len(r_t["properties"])):
            r_t = json_data["adverts"][i]["properties"][j]
            if r_t["name"] == "mileage_km":
                km = r_t["value"]
            if r_t["name"] == "engine_endurance":
                dimension = r_t["value"]
            if r_t["name"] == "engine_capacity":
                dimension = r_t["value"]
            if r_t["name"] == "engine_type":
                motor = r_t["value"].replace("пропан-бутан", "пр-бут")
            if r_t["name"] == "transmission_type":
                transmission = r_t["value"]
            if r_t["name"] == "color":
                color = r_t["value"]
            if r_t["name"] == "drive_type":
                drive = r_t["value"].replace("привод", "")
            if r_t["name"] == "body_type":
                typec = r_t["value"].replace("5 дв.", "").replace('грузопассажирский', 'гр.-пасс.')
            if r_t["name"] == "generation":
                generation = r_t["value"]
        if work is True:
            fresh_minutes = datetime.now() - datetime.strptime(published[:-8], "%Y-%m-%dT%H:%M")
            fresh_minutes = fresh_minutes.total_seconds() / 60
            if fresh_minutes <= WORK_PARSE_CARS_DELTA * 60 + 180:
                car.append([str(url), str(price)])
        else:
            car.append(
                [
                    str(url),
                    str("comments"),
                    f"{str(brand)} {str(model)} {str(generation)}",
                    str(price),
                    str(motor),
                    str(dimension),
                    str(transmission),
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


# -------------follow-price
def car_json_by_id(id_car):
    url = f"https://api.av.by/offers/{id_car}"
    try:
        r = requests.get(url, headers=HEADERS_JSON).json()
        return int(r["price"]["usd"]["amount"])
    except requests.exceptions.RequestException:
        return False
