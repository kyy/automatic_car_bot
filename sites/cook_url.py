import asyncio

from logic.database.config import database

from sites.abw.abw_cooking_urls import get_url_abw, abw_url_filter
from sites.abw.abw_parse_json import count_cars_abw

from sites.av.av_cooking_urls import get_url_av, av_url_filter
from sites.av.av_parse_json import count_cars_av

from sites.kufar.kufar_cooking_urls import get_url_kufar, kufar_url_filter
from sites.kufar.kufar_parse_json import count_cars_kufar

from sites.onliner.onliner_cooking_urls import get_url_onliner, onliner_url_filter
from sites.onliner.onliner_parse_json import count_cars_onliner


async def all_json(link, work=False):
    async with database() as db:

        return dict(
            av_json=asyncio.run(get_url_av(link, db)),
            abw_json=asyncio.run(get_url_abw(link, db)),
            onliner_json=asyncio.run(get_url_onliner(link, db)),
            kufar_json=asyncio.run(get_url_kufar(link, db, work)),
        )


def all_html(filter, json):
    """
    Получаем ссылки на человекочитаемые страницы
    :param filter: фильтр код из бд
    :param json: словарь с ссылками на json
    :return:
    """
    # сслыки на страницы с фильтром поиска
    av_link = av_url_filter(json['av_json'])
    onliner_link = onliner_url_filter(filter, json['onliner_json'])
    kufar_link = kufar_url_filter(json['kufar_json'])
    abw_link = abw_url_filter(json['abw_json'])

    return dict(
        av_link=av_link,
        onliner_link=onliner_link,
        abw_link=abw_link,
        kufar_link=kufar_link,
    )


def get_count_cars(json):
    # считаем сколько обявлений из json файлов
    all_cars_av = count_cars_av(json['av_json'])
    all_cars_abw = count_cars_abw(json['abw_json'])
    all_cars_onliner = count_cars_onliner(json['onliner_json'])
    all_cars_kufar = count_cars_kufar(json['kufar_json'])
    return dict(
        all_av=all_cars_av,
        all_abw=all_cars_abw,
        all_onliner=all_cars_onliner,
        all_kufar=all_cars_kufar,
    )


async def car_multidata(cars):
    # cars - фильтр-код
    json = await all_json(cars)
    count = get_count_cars(json)
    link = all_html(cars, json)
    return dict(
        json=json,
        count=count,
        link=link,
    )
