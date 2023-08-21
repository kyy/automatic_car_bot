import asyncio
from datetime import datetime, timedelta

import aiosqlite
import numpy as np
from tqdm import tqdm

from logic.constant import FSB, SS
from logic.database.config import database

data_now = datetime.today().date()   # сегодняшняя дата

subscription_days = timedelta(days=900)  # купленные дни

subscription_data = data_now + subscription_days    # пишем в БД дату окончнаия

current = abs(data_now - subscription_data)   # осталось дней

# if data_now > subscription_data:
#     print('Подписка истекла')
# else:
#     print('Подписка истечет через',  str(current).replace('days', 'дней').replace('day', 'день').split(',')[0])
#     print('Подписка истечет ',  subscription_data)
#
#
# string_data = '2026-01-31'
#
#
# newdata = datetime.strptime(string_data, "%Y-%m-%d").date()
# print(newdata)



# dim = {}
# [dim.update({j: i+1}) for i, j in enumerate([i for i in range(1000, 4100, 100)])]


dim_k = [i for i in range(1000, 4100, 100)]
dim_v = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 170, 173, 175, 180, 183, 190, 190, 200, 205, 205, 210, 211, 212, 213, 214, 220]
dim = dict(zip(dim_k, dim_v))

if __name__ == '__main__':
    print(dim)


