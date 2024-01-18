import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv('.env')

token = os.getenv('BOT_TOKEN')
BASE_URL = os.getenv('WH_BASE_URL')
WEB_SERVER_HOST = os.getenv('WH_SERVER_HOST')
WEB_SERVER_PORT = os.getenv('WH_SERVER_PORT')
MAIN_BOT_PATH = os.getenv('WH_PATH')

bot = Bot(token=token)
