import numpy as np
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from .keyboards import multi_row_keyboard
import datetime


router = Router()


def get_years(from_year=2000, to_year=datetime.datetime.now().year):
    years = [str(i) for i in range(from_year, to_year+1)]
    return years

def get_dimension(from_dim=1000, to_dim=9000):
    dim = [str(i/1000) for i in range(from_dim, to_dim+100, 100)]
    return dim

def get_cost(from_cost=5000, to_cost=35000, step=2500):
    cost = [str(i) for i in range(from_cost, to_cost+step, step)]
    return cost

motor = ['Бензин', 'Дизель', 'Электро']

transmission = ['Автомат', 'Механика']

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
    yearm_choosing = State()
    cost_choosing = State()
    costm_choosing = State()
    dimension_choosing = State()
    dimensionm_choosing = State()
    finish_choosing = State()


@router.message(Command(commands=["car"]))
async def brand_chosen(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_keyboard(get_brands(),
                                        input_field_placeholder='имя бренда')
    )
    await state.set_state(CreateCar.brand_choosing)


@router.message(CreateCar.brand_choosing)
async def model_chosen(message: Message, state: FSMContext):
    if message.text in get_brands():
        await state.update_data(chosen_brand=message.text)
        await message.answer(
            text="Теперь, выберите модель:",
            reply_markup=multi_row_keyboard(get_models(message.text),
                                            input_field_placeholder='имя модели')
        )
    else:
        await message.answer(
            text="Я не знаю такого бренда.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_brands(),
                                            input_field_placeholder='имя бренда')
        )
        return model_chosen
    await state.set_state(CreateCar.model_choosing)


@router.message(CreateCar.model_choosing)
async def motor_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in get_models(user_data['chosen_brand']):
        await state.update_data(chosen_model=message.text)
        await message.answer(
            text="Теперь, выберите тип топлива:",
            reply_markup=multi_row_keyboard(motor,
                                            input_field_placeholder='тип топлива')
        )
    else:
        await message.answer(
            text="Я не знаю такой модели.\n"
                 "Пожалуйста, выберите один из вариантов из списка ниже:",
            reply_markup=multi_row_keyboard(get_models(user_data['chosen_brand']),
                                            input_field_placeholder='имя модели')
        )
        return motor_chosen
    await state.set_state(CreateCar.motor_choosing)


@router.message(CreateCar.motor_choosing)
async def transmission_chosen(message: Message, state: FSMContext):
    if message.text in motor:
        await state.update_data(chosen_motor=message.text)
        await message.answer(
            text="Теперь, выберите тип трансмиссии:",
            reply_markup=multi_row_keyboard(transmission,
                                            input_field_placeholder='тип трансмиссии')
        )
    else:
        await message.answer(
            text="Я не знаю такого топлива.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(motor,
                                            input_field_placeholder='тип топлива')
        )
        return transmission_chosen
    await state.set_state(CreateCar.transmission_choosing)


@router.message(CreateCar.transmission_choosing)
async def from_year_chosen(message: Message, state: FSMContext):
    if message.text in transmission:
        await state.update_data(chosen_transmission=message.text)
        await message.answer(
            text="Теперь, выберите с какого года:",
            reply_markup=multi_row_keyboard(get_years(),
                                            input_field_placeholder='год от',
                                            columns=8
                                            )
        )
    else:
        await message.answer(
            text="Я не знаю такой трансмиссии.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(transmission,
                                            input_field_placeholder='тип трансмиссии')
        )
        return from_year_chosen
    await state.set_state(CreateCar.year_choosing)


@router.message(CreateCar.year_choosing)
async def to_year_chosen(message: Message, state: FSMContext):
    if message.text in get_years():
        await state.update_data(chosen_year_from=message.text)
        await message.answer(
            text="Теперь, выберите по какой год:",
            reply_markup=multi_row_keyboard(get_years(from_year=int(message.text)),
                                            input_field_placeholder='год по',
                                            columns=8
                                            )
        )
    else:
        await message.answer(
            text="Год от введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_years(),
                                            input_field_placeholder='год от')
        )
        return to_year_chosen
    await state.set_state(CreateCar.yearm_choosing)


@router.message(CreateCar.yearm_choosing)
async def min_cost_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in get_years(from_year=int(user_data['chosen_year_from'])):
        await state.update_data(chosen_year_to=message.text)
        await message.answer(
            text="Теперь, выберите начальную цену:",
            reply_markup=multi_row_keyboard(get_cost(),
                                            input_field_placeholder='стоимость от',
                                            columns=8
                                            )
        )
    else:
        await message.answer(
            text="Год до введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_years(from_year=int(user_data['chosen_year_from'])),
                                            input_field_placeholder='год по')
        )
        return min_cost_chosen
    await state.set_state(CreateCar.cost_choosing)


@router.message(CreateCar.cost_choosing)
async def max_cost_chosen(message: Message, state: FSMContext):
    if message.text in get_cost():
        await state.update_data(chosen_cost_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальную цену:",
            reply_markup=multi_row_keyboard(get_cost(from_cost=int(message.text)),
                                            input_field_placeholder='стоимость до',
                                            columns=8
                                            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_cost(),
                                            input_field_placeholder='стоимость от')
        )
        return max_cost_chosen
    await state.set_state(CreateCar.dimension_choosing)


@router.message(CreateCar.dimension_choosing)
async def min_dimension_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in get_cost(from_cost=int(user_data['chosen_cost_min'])):
        await state.update_data(chosen_cost_max=message.text)
        await message.answer(
            text="Теперь, выберите минимальный объем двигателя:",
            reply_markup=multi_row_keyboard(get_dimension(),
                                            input_field_placeholder='объем двигателя от',
                                            columns=8
                                            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_cost(from_cost=int(user_data['chosen_cost_min'])),
                                            input_field_placeholder='стоимость до')
        )
        return min_dimension_chosen
    await state.set_state(CreateCar.dimensionm_choosing)


@router.message(CreateCar.dimensionm_choosing)
async def max_dimension_chosen(message: Message, state: FSMContext):
    if message.text in get_dimension():
        await state.update_data(chosen_dimension_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальный объем двигателя:",
            reply_markup=multi_row_keyboard(get_dimension(from_dim=int(float(message.text)*1000)),
                                            input_field_placeholder='объем двигателя до',
                                            columns=8
                                            )
        )
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_dimension(),
                                            input_field_placeholder='объем двигателя от')
        )
        return max_dimension_chosen
    await state.set_state(CreateCar.finish_choosing)


@router.message(CreateCar.finish_choosing)
async def finish_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in get_dimension(from_dim=int(float(user_data['chosen_dimension_min'])*1000)):
        await state.update_data(chosen_dimension_max=message.text)
        choice = []
        user_data_up = await state.get_data()
        for item in user_data_up:
            choice.append(user_data_up[item])
        choice = ' '.join(choice)
        await message.answer(
            text=f"Вы выбрали - {choice} ",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_dimension(from_dim=int(float(user_data['chosen_dimension_min'])*1000)),
                                            input_field_placeholder='объем до')
        )
        return finish_chosen
