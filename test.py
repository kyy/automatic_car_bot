import asyncio
from datetime import datetime, timedelta

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



async def off_is_active(max_urls: int = 5, max_filters: int = 5, subs: bool = True) -> None:

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
        WHERE RowNum > 2 
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
        WHERE RowNum > 2 
        );
        
        """)

        await db.commit()



if __name__ == '__main__':
    asyncio.run(off_is_active())