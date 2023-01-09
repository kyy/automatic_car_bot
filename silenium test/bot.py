import asyncio
import copy
import logging
from aiogram import Bot, types, Dispatcher
from aiogram.utils import executor
from config import token
import numpy as np
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
from fpdf import FPDF
import os


bot = Bot(token=token)
dp = Dispatcher(bot)

def filter(car_input):
    # Входные параметры
    #car_input = 'Москвич 400 d a 1920 - 1000 15009 1400 2000'
    param_input = ['brands[0][brand]=', 'brands[0][model]=', 'engine_type[0]=', 'transmission_type=', 'year[min]=', 'year[max]=', 'price_usd[min]=', 'price_usd[max]=',
                            'engine_capacity[min]=', 'engine_capacity[max]=']

    # База данных
    car_input = dict(zip(param_input, car_input.split(' ')))
    transmission = {'a': '1', 'm': '2'}
    motor = {'b': '1', 'bpb': '2', 'bm': '3', 'bg': '4', 'd': '5', 'dg': '6', 'e': '7'}
    brands = np.load('brands_part_url.npy', allow_pickle=True).item()
    models = np.load(f'models_part_url/{car_input["brands[0][brand]="]}.npy', allow_pickle=True).item()

    # Корректируем данные для гет-запроса
    if car_input['brands[0][model]='] in models:
        car_input['brands[0][model]='] = models[car_input['brands[0][model]=']]
    if car_input['brands[0][brand]='] in brands:
        car_input['brands[0][brand]='] = brands[car_input['brands[0][brand]=']]
    if car_input['engine_type[0]='] in motor:
        car_input['engine_type[0]='] = motor[car_input['engine_type[0]=']]
    if car_input['transmission_type='] in transmission:
        car_input['transmission_type='] = transmission[car_input['transmission_type=']]

    new_part = []
    for key in car_input:
        if car_input[key] != '-':
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part)
    full_url = f'https://cars.av.by/filter?{new_part_url}'
    return full_url


def parse_cars(car_link):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103.0.0.0 Safari/537.36',
        'accept': '*/*'}
    r = requests.get(car_link)
    status_code = r.status_code
    if status_code == 200:
        r = r.content
        html = BeautifulSoup(r, "html.parser")
        links = html.select('.listing-item__link', headers=HEADERS)
        image = html.select('.listing-item__photo img')
        link_list = []
        image_list = []
        for l in links:
            link = l.get('href')
            link_list.append('https://cars.av.by'+link)
        for i in image:
            image = i.get('data-src')
            image_list.append(image)
        return dict(zip(link_list, image_list))
    else:
        print('неудача при попытке парсинга')
        print(status_code)
        if status_code == 503:
            time.sleep(7)
            parse_cars(car_link)


def pdf(dict, name):
    pdf = FPDF()
    pdf.add_page()
    for key in dict:
        pdf.image(f'{dict[key]}', x=None, y=None, w=190, h=0, type='', link=f'{key}')
    pdf.add_page()
    return pdf.output(f"{name}.pdf")

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nПример ввода\nМосквич 400 d a 1920 - 1000 15009 1400 2000\n команда в момощь - /brand")

@dp.message_handler(commands=['brand'])
async def process_start_command(message: types.Message):
    brands = np.load('brands_part_url.npy', allow_pickle=True).item()
    brands_out = []
    for brand in brands:
        brands_out.append(brand)
    brands_out.sort()
    brands_out = '   '.join(brands_out)
    await message.reply(brands_out)

@dp.message_handler()
async def cmd_test1(message: types.Message):
    try:
        cars = message.text
        car_link = filter(cars)
        dict = parse_cars(car_link)
        if len(dict) == 0:
            await message.reply("По вашему запросу ничего не найдено, или запрашиваемый сервер перегружен.\n"
                                "Если это сообщение появилось почти сразу, попробуйте повтоорить, время поиска занимает около 10 сек.")
        else:
            await message.reply(f"Найдено {len(dict)} автомобилей\nОжидайте .PDF файл")
            name_pdf_ = (str(datetime.now())).replace(':', '-')
            pdf(dict=dict, name=name_pdf_)
            await bot.send_document(chat_id=message.chat.id, document=open(f'{name_pdf_}.pdf', 'rb'))
            time.sleep(1)
            os.remove(f'{name_pdf_}.pdf')
    except Exception as error:
        await message.reply(f"Не удалось сформировать .PDF файл")
        print(error)



if __name__ == '__main__':
    executor.start_polling(dp)

