import requests
from bs4 import BeautifulSoup
import time


# av.by
def parse_cars(car_link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103.0.0.0 Safari/537.36',
        'accept': '*/*'}
    r = requests.get(car_link, headers=headers)
    status_code = r.status_code
    if status_code == 200:
        r = r.content
        html = BeautifulSoup(r, "lxml",)
        links = html.select('.listing-item__link')
        image = html.select('.listing-item__photo img')
        link_list = []
        image_list = []
        for lin in links:
            link = lin.get('href')
            link_list.append('https://cars.av.by'+link)
        for ima in image:
            image = ima.get('data-src')
            image_list.append(image)
        return dict(zip(link_list, image_list))
    else:
        print('Неудача при попытке парсинга\nПовторная попытка через 5 сек...')
        print(status_code)
        if status_code == 503:
            time.sleep(5)
            parse_cars(car_link)
