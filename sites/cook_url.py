import asyncio

from logic.database.config import database
from sites.av.av_cooking_urls import get_url_av, av_url_filter
from sites.kufar.kufar_cooking_urls import get_url_kufar, kufar_url_filter
from sites.abw.abw_cooking_urls import get_url_abw, abw_url_filter
from sites.onliner.onliner_cooking_urls import get_url_onliner, onliner_url_filter


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
