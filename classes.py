from aiogram import Bot
from aiogram.fsm.state import StatesGroup, State
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    BOT_TOKEN: str


config = Settings()

bot = Bot(token=config.BOT_TOKEN)


class CreateCar(StatesGroup):
    start_choosing = State()
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
    show_filter = State()
    add_url_stalk = State()
