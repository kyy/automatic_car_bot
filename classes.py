from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from config_reader import config


bot = Bot(token=config.BOT_TOKEN)


class CreateCar(StatesGroup):
    brand_choosing = State()
    model_choosing = State()
    motor_choosing = State()
    transmission_choosing = State()
    year_choosing = State()
    yearm_choosing = State()
    cost_choosing = State()
    costm_choosing = State()
    dimension_choosing = State()
    dimensionm_choosing = State()
    finish_choosing = State()
