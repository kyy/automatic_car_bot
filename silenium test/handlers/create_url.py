import numpy as np
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from .kbd_simple_row import single_row_keyboard, multi_row_keyboard
from pathlib import Path


router = Router()

available_food_sizes = ["Маленькую", "Среднюю", "Большую"]
brands_npy = np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item()

brands = []
for item in brands_npy:
    brands.append(item)
brands.sort()


def get_models(brand):
    path = Path(Path.cwd(), 'base_data_av_by', 'models_part_url', f'{brand}.npy')
    models_npy = np.load(path, allow_pickle=True).item()
    models = []
    for model in models_npy:
        models.append(model)
    models.sort()
    return models


class CreateCar(StatesGroup):
    brand_choosing = State()
    model_choosing = State()
    motor_choosing = State()
    transmission_choosing = State()
    year_choosing = State()
    cost_choosing = State()
    dimension_choosing = State()



@router.message(Command(commands=["car"]))
async def brand_chosen(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_keyboard(brands)
    )
    await state.set_state(CreateCar.brand_choosing)


@router.message(CreateCar.brand_choosing, F.text.in_(brands))
async def model_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_brand=message.text)
    brand = message.text
    await message.answer(
        text="Теперь, выберите модель:",
        reply_markup=multi_row_keyboard(get_models(brand))
    )
    await state.set_state(CreateCar.model_choosing)


@router.message(CreateCar.brand_choosing)
async def brand_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого бренда.\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=multi_row_keyboard(brands)
    )

@router.message(CreateCar.model_choosing) #добавить фильтр
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {user_data['chosen_brand']} {message.text}.\n",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(CreateCar.model_choosing)
async def food_size_chosen_incorrectly(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text="Я не знаю такого размера порции.\n"
             "Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=multi_row_keyboard(get_models(user_data['chosen_brand']))
    )
