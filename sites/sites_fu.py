import logging

from aiohttp import ClientSession

from logic.constant import FSB, MM, SS, FOLDER_PARSE, DOMEN
import os.path

from logic.database.config import database


async def sort_domens(url,  **kwargs):
    """
    
    :param url: 
    :param kwargs: 
    :return: 
    car_id: id from url
    """""

    split_url = url.split('/')
    domen = split_url[2]
    car_id = split_url[-1]

    async with ClientSession() as session:
        if DOMEN["AV"] in domen:
            params = await kwargs["av"](car_id, session)
        elif DOMEN["ONLINER"] in domen:
            params = await kwargs["onliner"](car_id, session)
        elif DOMEN["KUFAR"] in domen:
            params = await kwargs["kufar"](url, session)
        elif DOMEN["ABW"] in domen:
            params = await kwargs["abw"](url, session)

        return params


def max_min_params(car_input):
    car_input = car_input.split(SS)
    if car_input[4] == FSB:
        car_input[4] = str(MM["MIN_YEAR"])
    if car_input[5] == FSB:
        car_input[5] = str(MM["MAX_YEAR"])
    if car_input[6] == FSB:
        car_input[6] = str(MM["MIN_COST"])
    if car_input[7] == FSB:
        car_input[7] = str(MM["MAX_COST"])
    if car_input[8] == FSB:
        car_input[8] = str(MM["MIN_DIM"] * 1000)
    if car_input[9] == FSB:
        car_input[9] = str(MM["MAX_DIM"] * 1000)
    return car_input


def create_folders():
    if not os.path.exists(FOLDER_PARSE):
        try:
            os.mkdir(os.path.join('logic/database/', 'parse'))
        except Exception as e:
            logging.info(f'<sites_fu.create_folders> <parse folder> {e}')
    if not os.path.exists('logic/buffer'):
        try:
            os.mkdir(os.path.join('logic/', 'buffer'))
        except Exception as e:
            logging.info(f'<sites_fu.create_folders> <buffer folder> {e}')


async def json_urls():
    async with database() as db:
        av_urls_cursor = await db.execute(
            """
            SELECT url, id FROM ucars 
            WHERE LOWER(url) LIKE 'https://cars.av.by/%' AND is_active = 1""")
        av_urls = await av_urls_cursor.fetchall()
        av_urls = [(f"https://api.av.by/offers/{i[0].split('/')[-1]}", i[1]) for i in av_urls]
        onliner_urls_cursor = await db.execute(
            """
            SELECT url, id FROM ucars
            WHERE LOWER(url) LIKE 'https://ab.onliner.by/%' AND is_active = 1""")
        onliner_urls = await onliner_urls_cursor.fetchall()
        onliner_urls = [(f"https://ab.onliner.by/sdapi/ab.api/vehicles/{i[0].split('/')[-1]}", i[1]) for i in
                        onliner_urls]
        return [*av_urls, *onliner_urls]


async def html_urls():
    async with database() as db:
        kufar_abw_urls_cursor = await db.execute(
            """
            SELECT url, id FROM ucars
            WHERE (LOWER(url) LIKE 'https://auto.kufar.by/vi/%' OR LOWER(url) LIKE 'https://abw.by/cars/detail/%')
            AND is_active = 1""")
        kufar_abw_urls = await kufar_abw_urls_cursor.fetchall()
        kufar_abw_urls = [(i[0], i[1]) for i in kufar_abw_urls]
        return [*kufar_abw_urls]
