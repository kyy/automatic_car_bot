from datetime import datetime

from logic.constant import (SUBS_CARS_ADD_LIMIT, CARS_ADD_LIMIT, SUBS_FILTER_ADD_LIMIT,
                            FILTER_ADD_LIMIT, SUBS_CARS_ADD_LIMIT_ACTIVE, CARS_ADD_LIMIT_ACTIVE,
                            SUBS_FILTER_ADD_LIMIT_ACTIVE, FILTER_ADD_LIMIT_ACTIVE, SB)

from logic.database.config import database
from logic.text import TXT
from logic.kb_fu import get_years, get_cost, get_dimension


async def filter_import(callback, db):
    """
    :param callback:
    :param db:
    :return: id, fullfilter name, filter without 'filter='
    """
    filter_id = callback.data.split('_')[1]  # id фильтра
    async with db:
        select_filter_cursor = await db.execute("""SELECT search_param FROM udata WHERE id = $s""", (filter_id, ))
        filter_name = await select_filter_cursor.fetchone()  # фильтр-код ('filter=...',)
        cars = filter_name[0][7:]
    return filter_id, filter_name[0], cars


async def valid_params_filter_on_save(tel_id, data, bot):
    price_from = data['chosen_cost_min']
    price_to = data['chosen_cost_max']
    dimension_from = data['chosen_dimension_min']
    dimension_to = data['chosen_dimension_max']
    year_from = data['chosen_year_from']
    year_to = data['chosen_year_to']
    price_from = get_cost()[0] if price_from == SB else price_from
    price_to = get_cost()[-1] if price_to == SB else price_to
    dimension_from = get_dimension()[0] if dimension_from == SB else dimension_from
    dimension_to = get_dimension()[-1] if dimension_to == SB else dimension_to
    year_from = get_years()[0] if year_from == SB else year_from
    year_to = get_years()[-1] if year_to == SB else year_to

    status = all([int(price_from) < int(price_to),
                  float(dimension_from) <= float(dimension_to),
                  int(year_from) <= int(year_to)])

    if not status:
        await bot.send_message(tel_id, TXT['msg_wrong_filter'])

    return status


async def check_subs(user_id: int) -> bool:
    """
    Проверяем истекла ли подписка
    :param user_id: user.tel_id
    :return: True if subs is active
    """
    async with database() as db:
        subscription_data_cursor = await db.execute("""SELECT subs from user WHERE tel_id = $s""", (user_id,))
        subscription_data = await subscription_data_cursor.fetchone()[0]
        subscription_data = datetime.strptime(subscription_data, "%Y-%m-%d").date()
        data_now = datetime.today().date()
        return True if data_now < subscription_data else False


async def off_is_active() -> None:
    """
    Отключаем включенные фильтры и ссылки не более значений max_...
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
        WHERE RowNum > {CARS_ADD_LIMIT_ACTIVE}
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
        WHERE RowNum > {FILTER_ADD_LIMIT_ACTIVE}
        ) 
        """)
        await db.commit()


async def check_count_cars(tel_id, bot):
    """
    Подсчитываем кол-во ссылок пользвателя в отслеживании цен проверяем лимиты
    :param bot:
    :param tel_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute("""SELECT COUNT(ucars.id), user.vip FROM ucars
                                            INNER JOIN user on user.id = ucars.user_id
                                            WHERE user.tel_id = $s""", (tel_id,))
        user = await user_cursor.fetchone()
        count = user[0]
        vip = user[1]
        vip = 0 if vip is None else vip
        status = True if vip == 1 and count < SUBS_CARS_ADD_LIMIT or vip == 0 and count < CARS_ADD_LIMIT else False
        message = TXT['msg_limit_subs'] if vip == 1 else TXT['msg_limit']
        if not status:
            await bot.send_message(tel_id, message, disable_web_page_preview=True)
        return status


async def check_count_filters(tel_id, bot):
    """
    Подсчитываем кол-во фильтров пользвателя проверяем лимиты
    :param bot:
    :param tel_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute("""SELECT COUNT(udata.id), user.vip FROM udata
                                            INNER JOIN user on user.id = udata.user_id
                                            WHERE user.tel_id = $s""", (tel_id,))
        user = await user_cursor.fetchone()
        count = user[0]
        vip = user[1]
        vip = 0 if vip is None else vip
        status = True if vip == 1 and count < SUBS_FILTER_ADD_LIMIT or vip == 0 and count < FILTER_ADD_LIMIT else False
        message = TXT['msg_limit_subs'] if vip == 1 else TXT['msg_limit']
        if not status:
            await bot.send_message(tel_id, message, disable_web_page_preview=True)
        return status


async def check_count_cars_active(tel_id):
    """
    Отключает новые добавленные машины если лимит превышен
    :param tel_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute("""SELECT COUNT(ucars.id), user.vip FROM ucars
                                            INNER JOIN user on user.id = ucars.user_id
                                            WHERE user.tel_id = $s AND ucars.is_active = 1""", (tel_id,))
        user = await user_cursor.fetchone()
        count = user[0]
        vip = user[1]
        vip = 0 if vip is None else vip
        status = True if (vip == 1 and count < SUBS_CARS_ADD_LIMIT_ACTIVE) or \
                         (vip == 0 and count < CARS_ADD_LIMIT_ACTIVE) else False
        return status


async def check_count_filters_active(tel_id):
    """
    Отключает новые добавленные фильтры если лимит превышен
    :param tel_id: телеграм id
    :return: True если можно сохранить
    """
    async with database() as db:
        user_cursor = await db.execute("""SELECT COUNT(udata.id), user.vip FROM udata
                                            INNER JOIN user on user.id = udata.user_id
                                            WHERE user.tel_id = $s AND udata.is_active = 1""", (tel_id,))
        user = await user_cursor.fetchone()
        count = user[0]
        vip = user[1]
        vip = 0 if vip is None else vip
        status = True if (vip == 1 and count < SUBS_FILTER_ADD_LIMIT_ACTIVE) or\
                         (vip == 0 and count < FILTER_ADD_LIMIT_ACTIVE) else False
        return status


def strip_html(text):
    return (text.replace('True', '+')
                .replace('False', '-')
                .replace('=>', '')
                .replace('<=', '')
                .replace('->', '')
                .replace('<-', ''))
