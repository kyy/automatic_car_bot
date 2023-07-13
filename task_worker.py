import asyncio

import numpy as np
import pandas as pd
from aiogram import Bot
import aiosqlite
from arq import create_pool, cron
from arq.connections import RedisSettings
from b_logic.database.config import db_name
from b_logic.get_url_cooking import all_get_url
from b_logic.parse_cooking import parse_main
from config_reader import config

bot = Bot(token=config.bot_token.get_secret_value())


async def parse(ctx, car, message, name, work):
    av_link_json, abw_link_json, onliner_link_json = await all_get_url(car, work)
    parse_main(av_link_json, abw_link_json, onliner_link_json, message, name, work)


async def main(ctx):
    redis = await create_pool(RedisSettings())
    async with aiosqlite.connect(db_name) as db:
        select_cursor = await db.execute(f"""
        SELECT user.tel_id, udata.search_param, udata.id FROM udata
        INNER JOIN user on user.id = udata.user_id
        WHERE udata.is_active=1 
        ORDER BY user.tel_id ASC 
        """)
        select = await select_cursor.fetchall()
    for item in select:
        await redis.enqueue_job('parse', item[1][7:], item[0], item[2], True)
        await asyncio.sleep(0.3)
        try:
            open = pd.DataFrame(np.load(f'b_logic/buffer/{item[0]}_{item[2]}.npy', allow_pickle=True))
            links = open.iloc[0:, 0].tolist()
            print(links)
            if len(links) > 0:
                try:
                    await bot.send_message(item[0], str(links))
                except Exception as e:
                    print(e, f'Не удалось отправить сообщение {str(links)} \nпользователю {item[0]}')
        except Exception as e:
            print(e, f'Не удалось открыть файл {item[0]}_{item[2]}')



# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker

class WorkerSettings:
    functions = [parse]
    cron_jobs = [cron(main, hour={i for i in range(1, 24)}, minute={00})]


if __name__ == '__main__':
    asyncio.run(main())
