from aiogram.fsm import context

from config_reader import config
import asyncio
import logging
from aiogram import Bot, types, Dispatcher
from aiogram.types import FSInputFile
from config_reader import config
import time
from datetime import datetime
import numpy as np
import os
from do_pdf import do_pdf
from get_url import get_url
from parse import parse_cars
from aiogram.dispatcher.router import Router

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


# @dp.message(commands=['start'])
# async def process_start_command(message: types.Message):
#     await message.reply("Привет!\nПример ввода\nAudi/A6/d/a/2000/2023/0/50000/1400/5000\n показать бренды и модели - /brand")
#
# @dp.message(commands=['brand'])
# async def process_brand_command(message: types.Message):
#     brands = np.load('brands_part_url.npy', allow_pickle=True).item()
#     brands_out = []
#     for brand in brands:
#         brands_out.append(brand)
#     brands_out.sort()
#     brands_out = '   '.join(brands_out)
#     await message.reply(brands_out)

@dp.message()
async def input_pars(message: types.Message):
    cars = message.text
    car_link = get_url(cars)
    dicts = parse_cars(car_link)
    if len(dicts) == 0:
        await message.reply("По вашему запросу ничего не найдено, или запрашиваемый сервер перегружен.")
    else:
        try:
            await message.reply("Запрос принят")
            await message.reply(f"Найдено позиций - {len(dicts)}\nОжидайте .PDF файл")
            name_pdf_ = (str(datetime.now())).replace(':', '-')
            do_pdf(dict_=dicts, name=name_pdf_)
            file = FSInputFile(f'{name_pdf_}.pdf')
            await bot.send_document(message.chat.id, document=file)
            os.remove(f'{name_pdf_}.pdf')
        except Exception as error:
            await message.reply(f"Не удалось отправить .PDF файл")
            print(str(error))


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
