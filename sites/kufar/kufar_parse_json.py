import logging
from datetime import datetime
from lxml import etree

from logic.constant import (
    WORK_PARSE_CARS_DELTA,
    HEADERS_JSON,
    ROOT_URL,
    HEADERS,
    LEN_DESCRIPTION,
    KUFAR_WORK_PARSE_PRICE_DELTA_CORRECTION,
)
from logic.decorators import timed_lru_cache
from logic.text import TEXT_DETAILS


def html_parse_price_kufar(dom, url):
    price = dom.xpath('//*[@data-name="additional-price"]')[0].text
    price = price.replace(' ', '').replace('$*', '')
    return [[int(price), url]]


async def count_cars_kufar(url, session):
    if url is None:
        return 0
    try:
        async with session.get(url=url.replace("rendered-paginated?", "count?"), headers=HEADERS_JSON) as resp:
            r = await resp.json(content_type=None)
            return int(r["count"])
    except Exception as e:
        logging.error(f'<count_cars_kufar> {e}')
        return 0


@timed_lru_cache(300)
def json_links_kufar(url):
    if url == ROOT_URL['KUFAR']:
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
            if fresh_minutes <= WORK_PARSE_CARS_DELTA * 60 + KUFAR_WORK_PARSE_PRICE_DELTA_CORRECTION:
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


async def get_car_html(url, session):
    try:
        async with session.get(
                url=url,
                headers=HEADERS,
        ) as resp:
            r = await resp.text()
            return etree.HTML(str(r))
    except Exception as e:
        logging.error(f'<kufar_by.kufar_json_by_id> {e}')
        return False


async def kufar_research(id_car, session):
    dom = await get_car_html(id_car, session)
    price = dom.xpath('//*[@data-name="additional-price"]')[0].text
    price = price.replace(' ', '').replace('$*', '')
    city = dom.xpath('//*[@data-name="ad_region_listing"]')[0].text
    brand = dom.xpath('//*[@data-name="cars_brand_v2"]/following-sibling::node()[1]/span')[0].text
    try:
        model = dom.xpath('//*[@data-name="cars_model_v2"]/following-sibling::node()[1]/span')[0].text
    except:
        model = ''
    try:
        generation = dom.xpath('//*[@data-name="cars_gen_v2"]/following-sibling::node()[1]/span')[0].text
    except:
        generation = ''
    year = dom.xpath('//*[@data-name="regdate"]/following-sibling::node()[1]/span')[0].text
    km = dom.xpath('//*[@data-name="mileage"]/following-sibling::node()[1]/span')[0].text
    motor = dom.xpath('//*[@data-name="cars_engine"]/following-sibling::node()[1]/span')[0].text
    dimension = dom.xpath('//*[@data-name="cars_capacity"]/following-sibling::node()[1]/span')[0].text
    dimension = dimension.replace('л', '')
    transmission = dom.xpath('//*[@data-name="cars_gearbox"]/following-sibling::node()[1]/span')[0].text
    typec = dom.xpath('//*[@data-name="cars_type"]/following-sibling::node()[1]/span')[0].text
    try:
        drive = dom.xpath('//*[@data-name="cars_drive"]/following-sibling::node()[1]/span')[0].text
    except:
        drive = ''
    try:
        color = dom.xpath('//*[@data-name="cars_color"]/following-sibling::node()[1]/span')[0].text
    except:
        color = ''
    description = dom.xpath('//*[@itemprop="description"]/text()')
    descr = ' '.join(description)
    url = id_car
    vin = ''
    vin_check = ''
    status = ''
    days = ''

    text = TEXT_DETAILS.format(
        url=url, price=price, brand=brand, model=model, generation=generation, year=year, motor=motor,
        dimension=dimension, color=color, typec=typec, status=status, vin=vin, vin_check=vin_check, city=city,
        descr=descr[:LEN_DESCRIPTION], days=days, transmission=transmission, drive=drive, km=km,
    )
    return text


async def get_kufar_photo(url, session):
    dom = await get_car_html(url, session)
    photo = dom.xpath('//*[@class="swiper-zoom-container"]/img/@src')[0]
    return photo


async def get_kufar_stalk_name(url, session):
    dom = await get_car_html(url, session)
    try:
        brand = dom.xpath('//*[@data-name="cars_brand_v2"]/following-sibling::node()[1]/span')[0].text
        model = dom.xpath('//*[@data-name="cars_model_v2"]/following-sibling::node()[1]/span')[0].text
        price = dom.xpath('//*[@data-name="additional-price"]')[0].text
        price = price.replace(' ', '').replace('$*', '')
        return f'{brand} {model}', int(price)
    except Exception as e:
        logging.error(f'<get_kufar_stalk_name> kufar_url: {url} {e}')
        return ' '.join(url.split('/')[-2:]), 0
