# import random
# from datetime import datetime, timedelta
#
# data_now = datetime.today().date()  # сегодняшняя дата
# subscription_days = timedelta(days=900)  # купленные дни
# subscription_data = data_now + subscription_days  # пишем в БД дату окончнаия
# current = abs(data_now - subscription_data)  # осталось дней
#
# if data_now > subscription_data:
#     print('Подписка истекла')
# else:
#     print('Подписка истечет через', str(current).replace('days', 'дней').replace('day', 'день').split(',')[0])
#     print('Подписка истечет ', subscription_data)
#
# string_data = '2026-01-31'
#
# newdata = datetime.strptime(string_data, "%Y-%m-%d").date()
# print(newdata)
#
# sequence = 1, 2, 3
# a = random.choice(sequence)
import asyncio

import aiosqlite

from logic.database.config import database

tel_id = 32344234
ref_id = 514390056
async def gg():
    async with database() as db:
        check_id_cursor = await db.execute(f"SELECT tel_id FROM user WHERE tel_id = '{tel_id}'")
        check_id = await check_id_cursor.fetchone()
        if check_id is None:
            await db.executescript(
                f"INSERT INTO user (tel_id) VALUES ({tel_id});"
                f"UPDATE user SET ref = ref + 1 WHERE tel_id = {ref_id};")
            await db.commit()


if __name__ == '__main__':
    asyncio.run(gg())