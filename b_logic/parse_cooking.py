import asyncio
import numpy as np
from aiohttp import ClientSession
import nest_asyncio
from .source.av_by import json_links_av, bound_fetch_av
from .source.abw_by import json_links_abw, bound_fetch_abw
from .source.onliner_by import json_links_onliner, bound_fetch_onliner


nest_asyncio.apply()

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
}


async def run(urls_av, urls_abw, urls_onliner, result, work):
    tasks = []
    # Выбрал лок от балды. Можете поиграться.
    semaphore = asyncio.Semaphore(5)
    # Опять же оставляем User-Agent, чтобы не получить ошибку от Metacritic
    async with ClientSession(headers=headers) as session:

        if urls_av:
            for url in urls_av:
                task = asyncio.ensure_future(bound_fetch_av(semaphore, url, session, result, work))
                tasks.append(task)
        if urls_abw:
            for url in urls_abw:
                task = asyncio.ensure_future(bound_fetch_abw(semaphore, url, session, result, work))
                tasks.append(task)
        if urls_onliner:
            for url in urls_onliner:
                task = asyncio.ensure_future(bound_fetch_onliner(semaphore, url, session, result, work))
                tasks.append(task)
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)


def parse_main(url_av, url_abw, url_onliner,  message, name, work=False):
    result = []
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(json_links_av(url_av),
                                       json_links_abw(url_abw),
                                       json_links_onliner(url_onliner),
                                       result,
                                       work,
                                       )
                                   )
    loop.run_until_complete(future)
    np.save(f'b_logic/buffer/{message}_{name}.npy', result)
    return result


if __name__ == "__main__":
    pass
