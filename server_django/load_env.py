import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv('.env')

token = os.getenv('BOT_TOKEN')

bot = Bot(token=token)
