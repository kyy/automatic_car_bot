import numpy as np
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from .kbd_simple_row import multi_row_keyboard


router = Router()


def get_brands():
    brands_npy = np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item()
    brands = []
    # noinspection PyTypeChecker
    for item in brands_npy:
        brands.append(item)
    brands.sort()
    return brands


# noinspection PyTypeChecker
def get_models(brand):
    models_npy = np.load(f'base_data_av_by/models_part_url/{brand}.npy', allow_pickle=True).item()
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
        reply_markup=multi_row_keyboard(get_brands())
    )
    await state.set_state(CreateCar.brand_choosing)


@router.message(CreateCar.brand_choosing, F.text.in_(get_brands()))
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
        reply_markup=multi_row_keyboard(get_brands())
    )


@router.message(CreateCar.model_choosing)
async def brand_model_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in (get_models(user_data['chosen_brand'])):
        await message.answer(
            text=f"Вы выбрали {user_data['chosen_brand']} {message.text}.\n",
            reply_markup=ReplyKeyboardRemove()
                            )
    else:
        await message.answer(
            text="Я не знаю такой модели.\n"
                 "Пожалуйста, выберите один из вариантов из списка ниже:",
            reply_markup=multi_row_keyboard(get_models(user_data['chosen_brand']))
                            )
