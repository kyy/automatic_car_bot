import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import BotCommand
from config_reader import config
import handler_common
import handler_create_filter


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="car", description="Создать новый фильтр"),
        BotCommand(command='search', description='Отобразить текущий фильтр '),
        BotCommand(command="cancel", description="Прервать действие"),
        BotCommand(command="clear", description="Прервать и очистить фильтр"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", )
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    await set_commands(bot)
    dp.include_router(handler_common.router)
    dp.include_router(handler_create_filter.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
