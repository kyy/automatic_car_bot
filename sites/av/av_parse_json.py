import logging
from datetime import datetime
from logic.constant import (WORK_PARSE_CARS_DELTA, REPORT_PARSE_LIMIT_PAGES, HEADERS_JSON, PARSE_LIMIT_PAGES,
                            LEN_DESCRIPTION)
from logic.text import TEXT_DETAILS


def json_parse_price_av(json):
    return [[int(json['price']['usd']['amount']), str(json['publicUrl'])]]


def jd_av(r_t):
    try:
        photo = r_t["photos"][0]["big"]["url"]
    except:
        photo = ''

    published = r_t["publishedAt"]
    price = r_t["price"]["usd"]["amount"]
    url = r_t["publicUrl"]
    days = r_t["originalDaysOnSale"]  # дни в продаже
    exchange = r_t["exchange"]["label"].casefold().replace("Обмен ", "").replace(" обмен", "")
    city = r_t["shortLocationName"]
    year = r_t["year"]
    brand = r_t["properties"][0]["value"]
    model = r_t["properties"][1]["value"]

    try:
        descr = r_t["description"]
    except:
        descr = ''

    try:
        vin = r_t["metadata"]["vinInfo"]["vin"]
        vin_check = r_t["metadata"]["vinInfo"]["checked"]
    except:
        vin = vin_check = ''

    return dict(
        photo=photo,
        published=published,
        price=price,
        url=url,
        days=days,
        exchange=exchange,
        city=city,
        year=year,
        brand=brand,
        model=model,
        vin=vin,
        vin_check=vin_check,
        descr=descr,
    )


async def count_cars_av(url, session):
    try:
        async with session.get(url=url, headers=HEADERS_JSON) as resp:
            r = await resp.json(content_type=None)
            return int(r["count"])
    except Exception as e:
        logging.error(f'<count_cars_av> {e}')
        return 0


async def json_links_av(url, work, session):
    try:
        links_to_json = []
        async with session.get(url=url, headers=HEADERS_JSON) as resp:
            r = await resp.json(content_type=None)
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
        logging.error(f'<json_links_av> {e}')
        return False


def json_parse_av(json_data, work):
    car = []
    for i in range(len(json_data["adverts"])):
        r_t = json_data["adverts"][i]
        jd = jd_av(r_t)
        photo = jd["photo"]
        published = jd["published"]
        price = jd["price"]
        url = jd["url"]
        days = jd["days"]
        exchange = jd["exchange"]
        city = jd["city"]
        year = jd["year"]
        brand = jd["brand"]
        model = jd["model"]
        try:
            vin = jd["vin"]
        except:
            vin = ""
        generation = motor = dimension = transmission = km = typec = drive = color = ""

        for j in range(len(r_t["properties"])):
            r_t = json_data["adverts"][i]["properties"][j]
            if r_t["name"] == "brand":
                brand = r_t["value"]
            if r_t["name"] == "model":
                model = r_t["value"]
            if r_t["name"] == "generation":
                generation = r_t["value"]
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
                car.append([str(url), str(price), str(photo)])
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
async def av_json_by_id(id_car, session):
    try:
        async with session.get(
                url=f"https://api.av.by/offers/{id_car}",
                headers=HEADERS_JSON,
        ) as resp:
            return await resp.json(content_type=None)
    except Exception as e:
        logging.error(f'<av_by.av_json_by_id> {e}')
        return False


async def av_research(id_car, session):
    j = await av_json_by_id(id_car, session)
    jd = jd_av(j)
    days = jd["days"]
    status = j["publicStatus"]["label"]
    price = jd["price"]
    city = jd["city"]
    year = jd["year"]
    url = jd["url"]
    photo = jd["photo"]
    descr = jd["descr"]
    vin = jd["vin"]
    vin_check = jd["vin_check"]

    generation = model = brand = motor = dimension = drive = color = transmission = typec = km = ''
    for i in range(len(j["properties"])):
        r_t = j["properties"][i]
        if r_t["name"] == "brand":
            brand = r_t["value"]
        if r_t["name"] == "model":
            model = r_t["value"]
        if r_t["name"] == "generation":
            generation = r_t["value"]
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

    text = TEXT_DETAILS.format(
        url=url, price=price, brand=brand, model=model, generation=generation, year=year, motor=motor,
        dimension=dimension, color=color, typec=typec, status=status, vin=vin, vin_check=vin_check, city=city,
        descr=descr[:LEN_DESCRIPTION], days=days, transmission=transmission, drive=drive, km=km,
    )

    return text, photo
