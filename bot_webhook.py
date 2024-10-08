import logging
from typing import Any, Dict, Union

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.token import TokenValidationError, validate_token
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from bot.handlers import *
from bot.commands import commands
from load_env import token, BASE_URL, WEB_SERVER_PORT, WEB_SERVER_HOST, MAIN_BOT_PATH

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
    filename='logs/webhook.log',
    filemode='a'
)

"""
https://localtunnel.github.io/www/
fast test:
1. 'npm install -g localtunnel'
2. 'lt --port 8350'
3. copy url, paste to 'BASE_URL'
4. run webhook.py
"""

BASE_URL = BASE_URL
MAIN_BOT_TOKEN = token
WEB_SERVER_HOST = WEB_SERVER_HOST
WEB_SERVER_PORT = int(WEB_SERVER_PORT)
MAIN_BOT_PATH = MAIN_BOT_PATH


def is_bot_token(value: str) -> Union[bool, Dict[str, Any]]:
    try:
        validate_token(value)
    except TokenValidationError:
        return False
    return True


async def on_startup(bot: Bot):
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")
    await bot.set_my_commands(commands=commands)


def webhook():
    app = web.Application()
    session = AiohttpSession()
    bot_settings = {
        "token": MAIN_BOT_TOKEN, "session": session,
        "default": DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    }
    bot = Bot(**bot_settings)
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)  # FSM !
    dp.startup.register(on_startup)

    dp.include_router(handler_common.router)
    dp.include_router(handler_create_filter.router)
    dp.include_router(handler_callback.router)
    dp.include_router(handler_filters.router)
    dp.include_router(handler_price_tracking.router)
    dp.include_router(handler_edit_filter.router)
    dp.include_router(handler_admin.router)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=MAIN_BOT_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    webhook()
