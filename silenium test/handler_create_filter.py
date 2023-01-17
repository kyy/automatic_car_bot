import os
import numpy as np
from aiogram import Router, F
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command
from keyboards import multi_row_keyboard
from datetime import datetime as datatime_datatime
import datetime
from b_logic.get_url import get_url
from b_logic.parse import parse_av_by
from b_logic.do_pdf import do_pdf
from config_reader import config


router = Router()
bot = Bot(token=config.bot_token.get_secret_value())

# constants of columns:keyboards: max = 8, default = 4
columns_motor = 3
columns_years = 5
columns_cost = 5
columns_dimension = 8

# source of data for buttons
# make '' for delete button
skip_button = '-'

motor = [skip_button] + \
        ['бензин', 'дизель', 'электро', 'дизель (гибрид)', 'бензин (метан)', 'бензин (гибрид)', 'бензин (пропан-бутан)']

transmission = [skip_button] + ['автомат', 'механика']


def get_brands() -> list[str]:
    return sorted(np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item())


def get_models(brand: str) -> list[str]:
    return [skip_button] + sorted(np.load(f'base_data_av_by/models_part_url/{brand}.npy', allow_pickle=True).item())


def get_years(from_year: int = 1990, to_year=datetime.datetime.now().year) -> list[str]:
    return [skip_button] + [str(i) for i in range(from_year, to_year + 1)]


def get_dimension(from_dim: float = 1, to_dim: float = 9, step: float = 0.1) -> list[str]:
    return [skip_button] + [str(round(i, 1)) for i in np.arange(from_dim, to_dim + step, step)]


def get_cost(from_cost: int = 500, to_cost: int = 100000, step: int = 2500) -> list[str]:
    return [skip_button] + [str(i) for i in range(from_cost, to_cost - step, step)]


def encode_filter_short(string: str = None, lists: list = None, sep: str = ',', get_years = get_years, get_cost = get_cost, get_dimension = get_dimension, datetime = datetime):
    if lists == None: c = string.split(sep=sep)
    if str == None: c = lists
    return f"{c[0].replace('-', '<все бренды>')} {c[1].replace('-', '<все модели>')}\n" \
           f"{c[2].replace('-', '<все типы двигателей>')} {c[3].replace('-', '<все типы трансмиссий>')}\n" \
           f"с {c[4].replace('-', get_years()[1])}  по {c[5].replace('-', str(datetime.datetime.now().year))} г\n" \
           f"от {c[6].replace('-', get_cost()[1])}  до {c[7].replace('-', str(get_cost()[-1]))} $\n" \
           f"от {c[8].replace('-', get_dimension()[1])}  до {c[9].replace('-', str(get_dimension()[-1]))} л"




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


@router.message(F.text.startswith('filter='))
async def cooking_pdf(message: Message):
    if message.text[0:7] == 'filter=':
        cars = message.text.replace('filter=', '')
        car_link = get_url(cars)
        dicts = parse_av_by(car_link)
        if len(dicts) == 0:
            await message.answer("По вашему запросу ничего не найдено, или запрашиваемый сервер перегружен.")
        else:
            try:
                await message.answer("Запрос принят", reply_markup=ReplyKeyboardRemove())
                await message.reply(f"Найдено позиций - {len(dicts)}\nГотовим pdf файл")
                name_pdf_ = (str(datatime_datatime.now())).replace(':', '-')
                try:
                    do_pdf(data=dicts, name=name_pdf_, filter_full='dfsdf', filter_short=message.text)
                except Exception as error:
                    print(str(error), "<--> Ошибка при создании pdf")
                    return await message.answer("Ошибка при создании pdf")
                if os.path.exists(f'{name_pdf_}.pdf'):
                    file = FSInputFile(f'{name_pdf_}.pdf')
                    await bot.send_document(message.chat.id, document=file)
                    os.remove(f'{name_pdf_}.pdf')
                else:
                    print(f'{name_pdf_}.pdf не найден')
            except Exception as error:
                await message.answer(f"Не удалось отправить pdf файл")
                print(str(error))


@router.message(Command(commands=["search"]))
@router.message(F.text.casefold() == "search")
async def get_rusult(message: Message, state: FSMContext):
    await state.set_state('finish_choosing')
    data = await state.get_data()
    c = []
    for item in data:
        c.append(data[item])
    cc = c.copy()
    transmission = {'автомат': 'a', 'механика': 'm'}
    motor = {'бензин': 'b', 'бензин (пропан-бутан)': 'bpb', 'бензин (метан)': 'bm', 'бензин (гибрид)': 'bg',
             'дизель': 'd', 'дизель (гибрид)': 'dg', 'электро': 'e'}
    if len(cc) > 0:
        if cc[2] in motor:
            cc[2] = motor[cc[2]]
        if cc[3] in transmission:
            cc[3] = transmission[cc[3]]
        if cc[8] != '-':
            cc[8] = str(int(cc[8].replace('.', ''))*100)
        if cc[9] != '-':
            cc[9] = str(int(cc[9].replace('.', ''))*100)
    cc = 'filter=' + '|'.join(cc)
    if len(c) > 0 and c[0] != '-':
        await message.answer(text=encode_filter_short(lists=c), reply_markup=ReplyKeyboardRemove())
        await message.answer(text='фильтр-запрс:', reply_markup=multi_row_keyboard([cc,]))
        await cooking_pdf(message=message)
    else:
        await message.answer(
            text=f"Фильтр пуст. Воспользуйтесь командой /car",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(Command(commands=["car"]))
@router.message(F.text.casefold() == "car")
async def brand_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_brand=skip_button,
                            chosen_model=skip_button,
                            chosen_motor=skip_button,
                            chosen_transmission=skip_button,
                            chosen_year_from=skip_button,
                            chosen_year_to=skip_button,
                            chosen_cost_min=skip_button,
                            chosen_cost_max=skip_button,
                            chosen_dimension_min=skip_button,
                            chosen_dimension_max=skip_button,
                            )
    await message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_keyboard(get_brands(),
                                        input_field_placeholder='имя бренда',
                                        )
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
                                            input_field_placeholder='тип топлива',
                                            columns=columns_motor,
                                            )
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
                                            input_field_placeholder='тип топлива',
                                            columns=columns_motor,
                                            )
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
                                            columns=columns_years,
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
        year = get_years()[1] if message.text == skip_button else message.text
        await state.update_data(chosen_year_from=message.text)
        await message.answer(
            text="Теперь, выберите по какой год:",
            reply_markup=multi_row_keyboard(get_years(from_year=int(year)),
                                            input_field_placeholder='год по',
                                            columns=columns_years,
                                            )
        )
    else:
        await message.answer(
            text="Год от введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_years(),
                                            input_field_placeholder='год от',
                                            columns=columns_years,
                                            )
        )
        return to_year_chosen
    await state.set_state(CreateCar.yearm_choosing)


@router.message(CreateCar.yearm_choosing)
async def min_cost_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    year = get_years()[1] if skip_button == user_data['chosen_year_from'] else user_data['chosen_year_from']
    if message.text in get_years(from_year=int(year)):
        await state.update_data(chosen_year_to=message.text)
        await message.answer(
            text="Теперь, выберите начальную цену:",
            reply_markup=multi_row_keyboard(get_cost(),
                                            input_field_placeholder='стоимость от',
                                            columns=columns_cost,
                                            )
        )
    else:
        await message.answer(
            text="Год до введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_years(from_year=int(year)),
                                            input_field_placeholder='год по',
                                            columns=columns_years,
                                            )
        )
        return min_cost_chosen
    await state.set_state(CreateCar.cost_choosing)


@router.message(CreateCar.cost_choosing)
async def max_cost_chosen(message: Message, state: FSMContext):
    if message.text in get_cost():
        cost = get_cost()[1] if message.text == skip_button else message.text
        await state.update_data(chosen_cost_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальную цену:",
            reply_markup=multi_row_keyboard(get_cost(from_cost=int(cost)),
                                            input_field_placeholder='стоимость до',
                                            columns=columns_cost,
                                            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_cost(),
                                            input_field_placeholder='стоимость от',
                                            columns=columns_cost,
                                            )
        )
        return max_cost_chosen
    await state.set_state(CreateCar.dimension_choosing)


@router.message(CreateCar.dimension_choosing)
async def min_dimension_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    cost = get_cost()[1] if skip_button == user_data['chosen_cost_min'] else user_data['chosen_cost_min']
    if message.text in get_cost(from_cost=int(cost)):
        await state.update_data(chosen_cost_max=message.text)
        await message.answer(
            text="Теперь, выберите минимальный объем двигателя:",
            reply_markup=multi_row_keyboard(get_dimension(),
                                            input_field_placeholder='объем двигателя от',
                                            columns=columns_dimension,
                                            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_cost(from_cost=int(user_data['chosen_cost_min'])),
                                            input_field_placeholder='стоимость до',
                                            columns=columns_cost,
                                            )
        )
        return min_dimension_chosen
    await state.set_state(CreateCar.dimensionm_choosing)


@router.message(CreateCar.dimensionm_choosing)
async def max_dimension_chosen(message: Message, state: FSMContext):
    if message.text in get_dimension():
        dimension = get_dimension()[1] if message.text == skip_button else message.text
        await state.update_data(chosen_dimension_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальный объем двигателя:",
            reply_markup=multi_row_keyboard(get_dimension(from_dim=float(dimension)),
                                            input_field_placeholder='объем двигателя до',
                                            columns=columns_dimension,
                                            )
        )
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_dimension(),
                                            input_field_placeholder='объем двигателя от',
                                            columns=columns_dimension,
                                            )
        )
        return max_dimension_chosen
    await state.set_state(CreateCar.finish_choosing)


@router.message(CreateCar.finish_choosing)
async def finish_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dimension = get_dimension()[1] if skip_button == user_data['chosen_dimension_min'] \
        else user_data['chosen_dimension_min']
    if message.text in get_dimension(from_dim=float(dimension)):
        await state.update_data(chosen_dimension_max=message.text)
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(get_dimension(from_dim=float(user_data['chosen_dimension_min'])),
                                            input_field_placeholder='объем до', )
        )
        return finish_chosen
    await get_rusult(message=message, state=state)
