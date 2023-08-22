from datetime import datetime
from functools import lru_cache
from .decorators import timed_lru_cache
import numpy as np
from logic.constant import (SS, MOTOR_DICT, FSB, ROOT, MM, SUBS_CARS_ADD_LIMIT, CARS_ADD_LIMIT, SUBS_FILTER_ADD_LIMIT,
                            FILTER_ADD_LIMIT, SUBS_CARS_ADD_LIMIT_ACTIVE, CARS_ADD_LIMIT_ACTIVE,
                            SUBS_FILTER_ADD_LIMIT_ACTIVE, FILTER_ADD_LIMIT_ACTIVE)
from logic.database.config import database
from logic.cook_url import all_get_url
from logic.parse_sites.abw_by import count_cars_abw
from logic.parse_sites.av_by import count_cars_av
from logic.parse_sites.onliner_by import count_cars_onliner
from logic.parse_sites.kufar_by import count_cars_kufar
from .text import TXT
from aiocache import cached, Cache


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


def get_search_links(cars, json):
    # сслыки на страницы с фильтром поиска
    av_link = av_url_filter(json['av_json'])
    onliner_link = onliner_url_filter(cars, json['onliner_json'])
    kufar_link = kufar_url_filter(json['kufar_json'])
    abw_link = abw_url_filter(json['abw_json'])
    return dict(
        av_link=av_link,
        onliner_link=onliner_link,
        abw_link=abw_link,
        kufar_link=kufar_link,
    )


async def filter_import(callback, db):
    """
    :param callback:
    :param db:
    :return: id, fullfilter name, filter without 'filter='
    """
    filter_id = callback.data.split('_')[1]     # id фильтра
    async with db:
        select_filter_cursor = await db.execute(f"""SELECT search_param FROM udata WHERE id = {filter_id}""")
        filter_name = await select_filter_cursor.fetchone()     # фильтр-код ('filter=...',)
        cars = filter_name[0][7:]
    return filter_id, filter_name[0], cars


async def car_multidata(cars):
    # cars - фильтр-код
    json = await all_get_url(cars)
    count = get_count_cars(json)
    link = get_search_links(cars, json)
    return dict(
        json=json,
        count=count,
        link=link,
        )


@timed_lru_cache(300)
def av_url_filter(av_link_json):
    if av_link_json is None:
        return ROOT['AV']
    return f"https://cars.av.by/filter?{av_link_json.split('?')[1]}"


@timed_lru_cache(300)
def onliner_url_filter(car_input, onliner_link_json):
    """
    Ссылка на сайт
    :param car_input:фильтр-код 
    :param onliner_link_json: ссылка на json
    :return: 
    """
    if onliner_link_json is None:
        return ROOT['ONLINER']
    try:
        car = car_input.split(SS)
        brand, model = car[0:2]
        brands: dict = np.load('logic/database/parse/onliner_brands.npy', allow_pickle=True).item()
        link = onliner_link_json.split('vehicles?')[1]
        brand_slug = brands[brand][1]
        if model != FSB:
            models: dict = np.load('logic/database/parse/onliner_models.npy', allow_pickle=True).item()
            model_slug = models[brand][model][2]
            url = f'https://ab.onliner.by/{brand_slug}/{model_slug}?{link}'
        else:
            url = f'https://ab.onliner.by/{brand_slug}?{link}'
        return url
    except Exception as e:
        print('[func.onliner_url_filter]', e)
        return ROOT['ONLINER']


@timed_lru_cache(300)
def kufar_url_filter(kufar_link_json):
    if kufar_link_json is None:
        return ROOT['KUFAR']
    try:
        kuf = kufar_link_json.replace('&cmdl2', '').replace('&cbnd2', '').split('=category_2010.mark_')
        kufar_link = kuf[1].replace('_', '-').replace('.model', '')
        kufar_link1, kufar_link2 = kufar_link, ''
        if '&' in kufar_link:
            kufar_link = kufar_link.split('&', 1)
            kufar_link1, kufar_link2 = kufar_link[0], kufar_link[1]
        kuf = kuf[0].split('/')[-1]\
            .replace('rendered-paginated?cat=2010', '').replace('&typ=sell', '').replace('&cur=USD', '')
        kufar_link = f"https://auto.kufar.by/l/cars/{kufar_link1}?cur=USD{kuf}&{kufar_link2}"
        return kufar_link
    except Exception as e:
        print('[func.kufar_url_filter]', e)
        return ROOT['KUFAR']


def abw_url_filter(abw_link_json):
    if abw_link_json is None:
        return ROOT['ABW']
    try:
        abw_link = f"https://abw.by/cars{abw_link_json.split('list')[1]}"
        return abw_link
    except Exception as e:
        print('[func.abw_url_filter]', e)
        return ROOT['ABW']


@cached(ttl=300, cache=Cache.MEMORY, key='brands', namespace="get_brands")
async def get_brands() -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT [unique] FROM brands ORDER BY [unique]")
        rows = await cursor.fetchall()
        brands = []
        for brand in rows:
            brands.append(brand[0])
    return brands


@cached(ttl=300, cache=Cache.MEMORY, namespace="get_models")
async def get_models(brand: str) -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT models.[unique] FROM models "
                                  f"INNER JOIN brands on brands.id =  models.brand_id "
                                  f"WHERE brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        models = []
        for brand in rows:
            models.append(brand[0])
    return models


@lru_cache()
def get_years(
        from_year: int = MM['MIN_YEAR'],
        to_year=MM['MAX_YEAR']
) -> list[str]:
    return [str(i) for i in range(from_year, to_year + 1)]


@lru_cache()
def get_dimension(
        from_dim: float = MM['MIN_DIM'],
        to_dim: float = MM['MAX_DIM']+0.1,
        step: float = MM['STEP_DIM']
) -> list[str]:
    return [str(round(i, 1)) for i in np.arange(from_dim, to_dim, step)]


@lru_cache()
def get_cost(
        from_cost: int = MM['MIN_COST'],
        to_cost: int = MM['MAX_COST']+MM['STEP_COST'],
        step: int = MM['STEP_COST']
) -> list[str]:
    return [str(i) for i in range(from_cost, to_cost, step)]


# encode from strings = 'Citroen|C4|b|a|-|-|-|-|-|-' or list to full description
def decode_filter_short(string: str = None, lists: list = None, sep: str = SS):
    motor_dict_reverse = dict(zip(MOTOR_DICT.values(), MOTOR_DICT.keys()))
    if lists is None:
        c = (string.split(sep=sep))
        if c[2] in motor_dict_reverse:
            c[2] = motor_dict_reverse[c[2]]
        if c[8] != FSB:
            c[8] = str(int(c[8]) / 1000)
        if c[9] != FSB:
            c[9] = str(int(c[9]) / 1000)
        if c[3] != FSB:
            c[3] = 'автомат' if c[3] == 'a' else 'механика'
    else:
        c = lists
    text = f"{c[0].replace(FSB, 'все бренды')} | {c[1].replace(FSB, 'все модели')} | " \
           f"{c[2].replace(FSB, 'все двигатели')} | {c[3].replace(FSB, 'все трансмиссии')} | " \
           f"{c[4].replace(FSB, get_years()[0])}г | {c[5].replace(FSB, str(datetime.now().year))}г | " \
           f"{c[6].replace(FSB, get_cost()[0])}$ | {c[7].replace(FSB, str(get_cost()[-1]))}$ | " \
           f"{c[8].replace(FSB, get_dimension()[0])}л | {c[9].replace(FSB, str(get_dimension()[-1]))}л"
    return text if lists else text.replace('\n', ' | ')


# decode from lists of discription to 'filter=Citroen|C4|b|a|-|-|-|-|-|-'
def code_filter_short(cc: list = None):
    if cc[3] != FSB:
        cc[3] = 'a' if cc[3] == 'автомат' else 'm'
    if cc[2] in MOTOR_DICT:
        cc[2] = MOTOR_DICT[cc[2]]
    if cc[8] != FSB:
        cc[8] = str(int(cc[8].replace('.', '')) * 100)
    if cc[9] != FSB:
        cc[9] = str(int(cc[9].replace('.', '')) * 100)
    return 'filter=' + SS.join(cc)


def pagination(data: iter, name: str,  ikb, per_page=3, cur_page=1):
    """
    Разбиваем итерируемую последовательность на страницы
    :param data: our data
    :param name: cb_name indention
    :param cur_page: number of current page from callback
    :param per_page: number of items per page
    :param ikb: InlineKeyboardButton
    :return: data, buttons ([<<], [1/23], [>>]), del_pages (callback for correctly deleting)
    Handler example:
            @router.callback_query((F.data.endswith('{:param name}_prev')) | (F.data.endswith('{:param name}_next')))
            async def pagination_params(callback: CallbackQuery):
            async with database() as db:
                page = int(callback.data.split('_')[0])
                await callback.message.edit_text(
                    'keyboard',
                    reply_markup=await params_menu_kb(:param cur_page))
    """
    lsp = len(data)
    pages = (lsp // per_page + 1) if (lsp % per_page != 0) else (lsp // per_page)
    cb_next = 2
    cb_prev = pages
    buttons = []
    if lsp > per_page:
        if cur_page == 1:
            data = data[0:per_page]
        elif pages == cur_page:
            data = data[cur_page * per_page - per_page:]
            cb_next = 1
            cb_prev = pages - 1
        elif pages > cur_page > 1:
            data = data[cur_page * per_page - per_page:cur_page * per_page]
            cb_next = cur_page + 1
            cb_prev = cur_page - 1
        buttons = [ikb(text=TXT['btn_page_left'], callback_data=f'{cb_prev}_{name}_prev'),
                   ikb(text=f'{cur_page}/{pages}', callback_data=f'1_{name}_prev'),
                   ikb(text=TXT['btn_page_right'], callback_data=f'{cb_next}_{name}_next')]
    del_page = cur_page
    if cur_page == pages:
        del_page = pages - 1 if (lsp % per_page == 1) and cur_page > 1 else cur_page
    return data, buttons, del_page


async def check_subs(user_id: int) -> bool:
    """
    Проверяем истекла ли подписка
    :param user_id: user.tel_id
    :return: True if subs is active
    """
    async with database() as db:
        subscription_data_cursor = await db.execute(f"""SELECT subs from user WHERE tel_id = '{user_id}'""")
        subscription_data = await subscription_data_cursor.fetchone()[0]
        subscription_data = datetime.strptime(subscription_data, "%Y-%m-%d").date()
        data_now = datetime.today().date()
        return True if data_now < subscription_data else False


async def off_is_active(max_urls: int = 5, max_filters: int = 5) -> None:
    """
    Отключаем включенные фильтры и ссылки не более значений max_...
    :param max_urls: максимальное кол-во ссылок
    :param max_filters:  максимальное кол-во фильтров
    :return:
    """
    async with database() as db:
        await db.executescript(f"""
        UPDATE ucars SET is_active = 0
        WHERE id in (
            SELECT id
                FROM (
                    SELECT ucars.id,  ucars.user_id,
                         ROW_NUMBER()
                         OVER (
                         PARTITION BY user_id
                         ORDER BY ucars.id 
                         ) RowNum
                    FROM ucars
                    INNER JOIN user on user.id = ucars.user_id
                    WHERE  ucars.is_active = 1 AND vip = 0
                )
        WHERE RowNum > {max_urls}
        );
        
        UPDATE udata SET is_active = 0
        WHERE id in (
            SELECT id
                FROM (
                    SELECT udata.id,  udata.user_id,
                         ROW_NUMBER()
                         OVER (
                         PARTITION BY user_id
                         ORDER BY udata.id 
                         ) RowNum
                    FROM udata
                    INNER JOIN user on user.id = udata.user_id
                    WHERE  udata.is_active = 1 AND vip = 0
                )
        WHERE RowNum > {max_filters}
        ) 
        """)
        await db.commit()


async def check_count_cars(u_id, bot):
    """
    Подсчитываем кол-во ссылок пользвателя в отслеживании цен проверяем лимиты
    :param u_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute(f"""SELECT COUNT(ucars.id), user.vip FROM ucars
                                            INNER JOIN user on user.id = ucars.user_id
                                            WHERE user.tel_id = {u_id}""")
        user = await user_cursor.fetchone()
        count = user[0]
        vip = user[1]
        status = True if vip == 1 and count < SUBS_CARS_ADD_LIMIT or vip == 0 and count < CARS_ADD_LIMIT else False
        limit = SUBS_CARS_ADD_LIMIT if vip == 1 else CARS_ADD_LIMIT
        message = TXT['msg_cars_limit_subs'] if vip == 1 else TXT['msg_cars_limit']
        if not status:
            await bot.send_message(u_id, message.format(limit=limit), disable_web_page_preview=True)
        return status


async def check_count_filters(u_id, bot):
    """
    Подсчитываем кол-во фильтров пользвателя проверяем лимиты
    :param u_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute(f"""SELECT COUNT(udata.id), user.vip FROM udata
                                            INNER JOIN user on user.id = udata.user_id
                                            WHERE user.tel_id = {u_id}""")
        user = await user_cursor.fetchone()
        count = user[0]
        vip = user[1]
        status = True if vip == 1 and count < SUBS_FILTER_ADD_LIMIT or vip == 0 and count < FILTER_ADD_LIMIT else False
        limit = SUBS_FILTER_ADD_LIMIT if vip == 1 else FILTER_ADD_LIMIT
        message = TXT['msg_filter_limit_subs'] if vip == 1 else TXT['msg_filter_limit']
        if not status:
            await bot.send_message(u_id, message.format(limit=limit), disable_web_page_preview=True)
        return status


async def check_count_cars_active(u_id):
    """
    Отключает новые добавленные машины если лимит превышен
    :param u_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute(f"""SELECT COUNT(ucars.id), user.vip FROM ucars
                                            INNER JOIN user on user.id = ucars.user_id
                                            WHERE user.tel_id = {u_id} AND ucars.is_active = 1""")
        user = await user_cursor.fetchone()
        count = user[0]
        print(user)
        vip = user[1]
        status = True if vip == 1 and count < SUBS_CARS_ADD_LIMIT_ACTIVE or vip == 0 and count < CARS_ADD_LIMIT_ACTIVE else False
        return status


async def check_count_filters_active(u_id):
    """
    Отключает новые добавленные фильтры если лимит превышен
    :param u_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute(f"""SELECT COUNT(udata.id), user.vip FROM udata
                                            INNER JOIN user on user.id = udata.user_id
                                            WHERE user.tel_id = {u_id} AND udata.is_active = 1""")
        user = await user_cursor.fetchone()
        count = user[0]
        vip = user[1]
        status = True if vip == 1 and count < SUBS_FILTER_ADD_LIMIT_ACTIVE or vip == 0 and count < FILTER_ADD_LIMIT_ACTIVE else False
        return status
