import logging
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiohttp.web import run_app
from aiohttp import web
import handler_common
import handler_create_filter
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from handler_common import set_commands
from config_reader import config


async def on_startup(bot: Bot, base_url: str):
    await bot.set_webhook(f"{base_url}/webhook")


bot = Bot(token=config.bot_token.get_secret_value())
dispatcher = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)
#await set_commands(bot)
dispatcher["base_url"] = config.deta_url.get_secret_value()
dispatcher.startup.register(on_startup)
dispatcher.include_router(handler_common.router)
dispatcher.include_router(handler_create_filter.router)
app = web.Application()
app["bot"] = bot
SimpleRequestHandler(dispatcher=dispatcher, bot=bot).register(app, path="/webhook")
setup_application(app, dispatcher, bot=bot)
logging.basicConfig(level=logging.INFO)
run_app(app)
