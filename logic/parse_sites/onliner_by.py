import logging
from datetime import datetime
import requests
from logic.constant import WORK_PARSE_CARS_DELTA, REPORT_PARSE_LIMIT_PAGES, HEADERS_JSON, PARSE_LIMIT_PAGES
from logic.decorators import timed_lru_cache


@timed_lru_cache(300)
def count_cars_onliner(url):
    if url is None:
        return 0
    try:
        r = requests.get(url, headers=HEADERS_JSON).json()
        count = int(r["total"])
        return count
    except Exception as e:
        logging.error(f'<count_cars_onliner> {e}')
        return 0


@timed_lru_cache(300)
def json_links_onliner(url, work):
    try:
        links_to_json = []
        r = requests.get(url, headers=HEADERS_JSON).json()
        page_count = r["page"]["last"]
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
        logging.error(f'<json_links_onliner> {e}')
        return False


def json_parse_onliner(json_data, work):
    car = []
    for i in range(len(json_data["adverts"])):
        r_t = json_data["adverts"][i]
        photo = 'https://via.placeholder.com/250x200'
        published = r_t["created_at"]
        price = r_t["price"]["converted"]["USD"]["amount"].split(".")[0]
        url = r_t["html_url"]
        brand_model_gen = r_t["title"]
        days = (datetime.now().date() - datetime.strptime(r_t["created_at"].split("T")[0], "%Y-%m-%d").date()).days
        city = r_t["location"]["city"]["name"]
        vin = ""
        exchange = ""
        year = r_t["specs"]["year"]
        km = r_t["specs"]["odometer"]["value"]
        dimension = str(r_t["specs"]["engine"]["capacity"]).replace("None", "")
        motor = (
            r_t["specs"]["engine"]["type"]
            .replace("gasoline", "бензин")
            .replace("diesel", "дизель")
            .replace("electric", "электро")
        )
        transmis = r_t["specs"]["transmission"].replace("mechanical", "механика").replace("automatic", "автомат")
        color = (
            r_t["specs"]["color"]
            .replace("skyblue", "св-синий")
            .replace("red", "красный")
            .replace("black", "черный")
            .replace("white", "белый")
            .replace("silver", "серебро")
            .replace("grey", "серый")
            .replace("blue", "синий")
            .replace("orange", "апельсин")
            .replace("other", "другой")
            .replace("brown", "коричневый")
        )
        drive = (
            r_t["specs"]["drivetrain"].replace("front", "передний").replace("all", "полный").replace("rear", "задний")
        )
        typec = (
            r_t["specs"]["body_type"]
            .replace("suv", "внедорожник")
            .replace("hatchback", "хачбек")
            .replace("sedan", "седан")
            .replace("universal", "универсал")
            .replace("minivan", "минивен")
            .replace("cabriolet", "кабриолет")
            .replace("liftback", "лифтбек")
            .replace("minibus", "миниавтобус")
        )
        brand = r_t['manufacturer']['name']
        model = r_t['model']['name']
        generation = r_t['generation']['name']
        if work is True:
            fresh_minutes = datetime.now() - datetime.strptime(published[:-9], "%Y-%m-%dT%H:%M")
            fresh_minutes = fresh_minutes.total_seconds() / 60

            if fresh_minutes <= WORK_PARSE_CARS_DELTA * 60:
                car.append([str(url), str(price), str(photo)])
        else:
            car.append(
                [
                    str(url),
                    "comment",
                    f"{str(brand_model_gen)}",
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


# -------------follow-price
def onliner_json_by_id(id_car):
    url = f"https://ab.onliner.by/sdapi/ab.api/vehicles/{id_car}"
    try:
        return requests.get(url, headers=HEADERS_JSON).json()
    except requests.exceptions.RequestException:
        return False
