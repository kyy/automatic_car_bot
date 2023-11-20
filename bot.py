import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from handlers import *
from bot_config import bot
from commands import commands


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
        filename='app.log',
        filemode='a'
    )
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)  # FSM !
    await bot.set_my_commands(commands=commands)

    dp.include_router(handler_common.router)
    dp.include_router(handler_create_filter.router)
    dp.include_router(handler_callback.router)
    dp.include_router(handler_filters.router)
    dp.include_router(handler_price_tracking.router)
    dp.include_router(handler_edit_filter.router)
    dp.include_router(handler_admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
