import asyncio
from aiohttp import ClientSession
import csv
import requests
import json
from multiprocessing import Pool
from time import sleep
from lxml import html
from bs4 import BeautifulSoup


source = 'https://habr.com/ru/post/319966/'
root = 'https://av.by/'
url = 'https://cars.av.by/peugeot'


def get_pages(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103.0.0.0 Safari/537.36',
        'accept': '*/*'}
    r = requests.get(url, headers=headers)
    r = r.content
    html = BeautifulSoup(r, "lxml", )
    link_list = []
    try:
        link = html.select('.listing-item__link')
        for lin in link:
            link = lin.get('href')
            link_list.append('https://cars.av.by' + link)
    except:
        pass
    return link_list


# def main():
#     # Загружаем ссылки на страницы жанров из нашего .json файла.
#     dict = json.load(open('genres.json', 'r'))
#     p = Pool(4)
#     # Простой пул. Функцией map отдаем каждому потоку его порцию жанров для парсинга.
#     p.map(get_pages, [dict[key] for key in dict.keys()])
#     print('Over')
#
# if __name__ == "__main__":
#     main()





result = []

total_checked = 0

async def get_one(url, session):
    global total_checked
    async with session.get(url) as response:
        # Ожидаем ответа и блокируем таск.
        page_content = await response.read()
        # Получаем информацию об игре и сохраняем в лист.
        item = get_item(page_content, url)
        result.append(item)
        total_checked += 1
        print('Inserted: ' + url + '  - - - Total checked: ' + str(total_checked))


async def bound_fetch(sm, url, session):
    try:
        async with sm:
            await get_one(url, session)
    except Exception as e:
        print(e)
        # Блокируем все таски на 30 секунд в случае ошибки 429.
        sleep(30)


async def run(urls):
    tasks = []
    # Выбрал лок от балды. Можете поиграться.
    sm = asyncio.Semaphore(25)
    headers = {"User-Agent": "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"}
    # Опять же оставляем User-Agent, чтобы не получить ошибку от Metacritic
    async with ClientSession(
            headers=headers) as session:
        for url in urls:
            # Собираем таски и добавляем в лист для дальнейшего ожидания.
            task = asyncio.ensure_future(bound_fetch(sm, url, session))
            tasks.append(task)
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)


def get_item(content, url):
    html = BeautifulSoup(content, "lxml", )
    params = html.find('div', class_='card__params').text
    return {'info':params,
            'url':url
    }


def main():
    # Запускаем наш парсер.
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(get_pages(url)))
    loop.run_until_complete(future)
    # Выводим результат. Можете сохранить его куда-нибудь в файл.
    print(result)
    print('Over')

if __name__ == "__main__":
    main()