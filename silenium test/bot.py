import asyncio
import logging
from aiogram import Bot, types, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import FSInputFile, BotCommand
from aiogram.filters import Command
from config_reader import config
from b_logic.do_pdf import do_pdf
from b_logic.get_url import get_url
from b_logic.parse import parse_cars
from datetime import datetime
from handlers import common, create_url
import numpy as np
import os


commands = [
        BotCommand(command="car", description="Фильтр поиска"),
        BotCommand(command="cancel", description="Прервать | Очистить выбранные шаги"),
        BotCommand(command='search', description='Пропустить шаги | Повторить поиск'),
        ]


async def set_commands(bot: Bot):
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", )
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    await set_commands(bot)
    dp.include_router(common.router)
    dp.include_router(create_url.router)


    # @dp.message(Command(commands=['brand']))
    # async def process_brand_command(message: types.Message):
    #     brands = np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item()
    #     brands_out = []
    #     for brand in brands:
    #         brands_out.append(brand)
    #     brands_out.sort()
    #     brands_out = '   '.join(brands_out)
    #     await message.answer(brands_out)
    #


    # @dp.message()
    # async def input_pars(message: types.Message):
    #     cars = message.text
    #     car_link = get_url(cars)
    #     dicts = parse_cars(car_link)
    #     if len(dicts) == 0:
    #         await message.reply("По вашему запросу ничего не найдено, или запрашиваемый сервер перегружен.")
    #     else:
    #         try:
    #             await message.reply("Запрос принят")
    #             await message.reply(f"Найдено позиций - {len(dicts)}\nОжидайте .PDF файл")
    #             name_pdf_ = (str(datetime.now())).replace(':', '-')
    #             do_pdf(dict_=dicts, name=name_pdf_)
    #             file = FSInputFile(f'{name_pdf_}.pdf')
    #             await bot.send_document(message.chat.id, document=file)
    #             os.remove(f'{name_pdf_}.pdf')
    #         except Exception as error:
    #             await message.reply(f"Не удалось отправить .PDF файл")
    #             print(str(error))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())
