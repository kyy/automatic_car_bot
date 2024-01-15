import logging
from typing import Any, Dict, Union

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.token import TokenValidationError, validate_token
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.handlers import *
from load_env import token

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
    filename='logs/webhook.log',
    filemode='a'
)
logging.info('start')
"""
https://localtunnel.github.io/www/
fast test:
1. 'npm install -g localtunnel'
2. 'lt --port 8350'
3. copy url, paste to 'BASE_URL'
4. run webhook.py
"""

BASE_URL = "https://mush.by"
MAIN_BOT_TOKEN = token
WEB_SERVER_HOST = "::"
WEB_SERVER_PORT = 8443
MAIN_BOT_PATH = "/web_hook"


def is_bot_token(value: str) -> Union[bool, Dict[str, Any]]:
    try:
        validate_token(value)
    except TokenValidationError:
        return False
    return True


async def on_startup(bot: Bot):
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")


def webhook():
    app = web.Application()
    session = AiohttpSession()
    bot_settings = {"token": MAIN_BOT_TOKEN, "session": session, "parse_mode": "Markdown"}
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
