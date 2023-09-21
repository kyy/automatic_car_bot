import logging

from aiohttp import ClientSession

from logic.database.config import database

from sites.abw.abw_cooking_urls import get_url_abw, abw_url_filter
from sites.abw.abw_parse_json import count_cars_abw, json_links_abw, get_abw_stalk_name, get_abw_photo

from sites.av.av_cooking_urls import get_url_av, av_url_filter
from sites.av.av_parse_json import count_cars_av, json_links_av, av_research, get_av_photo, get_av_stalk_name

from sites.kufar.kufar_cooking_urls import get_url_kufar, kufar_url_filter
from sites.kufar.kufar_parse_json import (
    count_cars_kufar, json_links_kufar, kufar_research, get_kufar_photo, get_kufar_stalk_name,
)
from sites.onliner.onliner_cooking_urls import get_url_onliner, onliner_url_filter
from sites.onliner.onliner_parse_json import (
    count_cars_onliner, json_links_onliner, onliner_research, get_onliner_photo, get_onliner_stalk_name,
)
from sites.sites_fu import sort_domens


async def all_json(link, work=False):
    async with database() as db:
        return dict(
            av_json=await get_url_av(link, db),
            abw_json=await get_url_abw(link, db),
            onliner_json=await get_url_onliner(link, db),
            kufar_json=await get_url_kufar(link, db, work),
        )


def all_html(filt, json):
    """
    Получаем ссылки на человекочитаемые страницы
    :param filt: фильтр код из бд
    :param json: словарь с ссылками на json
    :return:
    """
    # сслыки на страницы с фильтром поиска
    return dict(
        av_link=av_url_filter(json['av_json']),
        onliner_link=onliner_url_filter(filt, json['onliner_json']),
        abw_link=abw_url_filter(json['abw_json']),
        kufar_link=kufar_url_filter(json['kufar_json']),
    )


async def get_count_cars(json):
    # считаем сколько обявлений из json файлов
    async with ClientSession() as session:
        return dict(
            all_av=await count_cars_av(json['av_json'], session),
            all_abw=await count_cars_abw(json['abw_json'], session),
            all_onliner=await count_cars_onliner(json['onliner_json'], session),
            all_kufar=await count_cars_kufar(json['kufar_json'], session),
        )


async def car_multidata(cars):
    # cars - фильтр-код
    json = await all_json(cars)
    count = await get_count_cars(json)
    link = all_html(cars, json)

    return dict(
        json=json,
        count=count,
        link=link,
    )


async def urls_json(json, work):
    av = json["av_json"]
    onliner = json["onliner_json"]
    kufar = json["kufar_json"]
    abw = json["abw_json"]

    cars = []

    async with ClientSession() as session:
        if av:
            links_av = await json_links_av(av, work, session)
            if links_av:
                cars.extend([*links_av])

        if onliner:
            links_onliner = await json_links_onliner(onliner, work, session)
            if links_onliner:
                cars.extend([*links_onliner])

        if kufar:
            links_kufar = json_links_kufar(kufar)
            if links_kufar:
                cars.extend([*links_kufar])

        if abw:
            links_abw = await json_links_abw(abw, session)
            if links_abw:
                cars.extend([*links_abw])

    return cars


async def get_car_details(url, **kwargs):
    try:
        params = await sort_domens(url,
                                   av=av_research,
                                   onliner=onliner_research,
                                   kufar=kufar_research,
                                   **kwargs,
                                   )
        return params
    except Exception as e:
        logging.error(f'<sites_get_data.get_car_details> {e}')
        return False


async def get_photos(url, **kwargs):
    try:
        params = await sort_domens(url,
                                   av=get_av_photo,
                                   onliner=get_onliner_photo,
                                   kufar=get_kufar_photo,
                                   abw=get_abw_photo,
                                   **kwargs,
                                   )
        return params
    except Exception as e:
        logging.error(f'<sites_get_data.get_photos> {e}')
        return False


async def get_br_mod_pr(url, **kwargs):
    try:
        params = await sort_domens(url,
                                   av=get_av_stalk_name,
                                   onliner=get_onliner_stalk_name,
                                   kufar=get_kufar_stalk_name,
                                   abw=get_abw_stalk_name,
                                   **kwargs,
                                   )
        return params
    except Exception as e:
        logging.error(f'<sites_get_data.get_stalk_name> {e}')
        return False
