import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from lxml import etree
import aiosqlite
import numpy as np
import requests
from tqdm import tqdm
from logic.constant import FSB, SS, HEADERS, ROOT, SUBS_CARS_ADD_LIMIT_ACTIVE, CARS_ADD_LIMIT_ACTIVE
from logic.database.config import database

data_now = datetime.today().date()   # сегодняшняя дата
subscription_days = timedelta(days=900)  # купленные дни
subscription_data = data_now + subscription_days    # пишем в БД дату окончнаия
current = abs(data_now - subscription_data)   # осталось дней

if data_now > subscription_data:
    print('Подписка истекла')
else:
    print('Подписка истечет через',  str(current).replace('days', 'дней').replace('day', 'день').split(',')[0])
    print('Подписка истечет ',  subscription_data)


string_data = '2026-01-31'


newdata = datetime.strptime(string_data, "%Y-%m-%d").date()
print(newdata)




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

if __name__ == '__main__':

    asyncio.run(check_count_cars_active(514390056))

