import asyncio
from aiohttp import ClientSession
from logic.constant import LEN_DESCRIPTION
from logic.text import TEXT_DETAILS
from sites.kufar import get_car_html


async def kufar_research(id_car, session):
    dom = await get_car_html(id_car, session)
    price = dom.xpath('//*[@data-name="additional-price"]')[0].text
    price = price.replace(' ', '').replace('$*', '')
    city = dom.xpath('//*[@data-name="ad_region_listing"]')[0].text
    brand = dom.xpath('//*[@data-name="cars_brand_v2"]/following-sibling::node()[1]/span')[0].text
    model = dom.xpath('//*[@data-name="cars_model_v2"]/following-sibling::node()[1]/span')[0].text
    try:
        generation = dom.xpath('//*[@data-name="cars_gen_v2"]/following-sibling::node()[1]/span')[0].text
    except: generation = ''
    year = dom.xpath('//*[@data-name="regdate"]/following-sibling::node()[1]/span')[0].text
    km = dom.xpath('//*[@data-name="mileage"]/following-sibling::node()[1]/span')[0].text
    motor = dom.xpath('//*[@data-name="cars_engine"]/following-sibling::node()[1]/span')[0].text
    dimension = dom.xpath('//*[@data-name="cars_capacity"]/following-sibling::node()[1]/span')[0].text
    dimension = dimension.replace('л', '')
    transmission = dom.xpath('//*[@data-name="cars_gearbox"]/following-sibling::node()[1]/span')[0].text
    typec = dom.xpath('//*[@data-name="cars_type"]/following-sibling::node()[1]/span')[0].text
    try:
        drive = dom.xpath('//*[@data-name="cars_drive"]/following-sibling::node()[1]/span')[0].text
    except: drive = ''
    try:
        color = dom.xpath('//*[@data-name="cars_color"]/following-sibling::node()[1]/span')[0].text
    except: color = ''
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

async def main():
    async with ClientSession() as session:
        await kufar_research('https://auto.kufar.by/vi/214806452', session)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
