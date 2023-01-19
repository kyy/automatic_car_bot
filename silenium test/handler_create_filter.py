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

motor_dict = {'бензин': 'b', 'бензин (пропан-бутан)': 'bpb', 'бензин (метан)': 'bm', 'бензин (гибрид)': 'bg',
              'дизель': 'd', 'дизель (гибрид)': 'dg', 'электро': 'e'}

s_b = '-'    # skip button on keyboards

motor = [s_b] + \
        ['бензин', 'дизель', 'электро', 'дизель (гибрид)', 'бензин (метан)', 'бензин (гибрид)', 'бензин (пропан-бутан)']

transmission = [s_b] + ['автомат', 'механика']


def get_brands() -> list[str]:
    return sorted(np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item())


def get_models(brand: str) -> list[str]:
    return [s_b] + sorted(np.load(f'base_data_av_by/models_part_url/{brand}.npy', allow_pickle=True).item())


def get_years(from_year: int = 1990, to_year=datetime.datetime.now().year) -> list[str]:
    return [s_b] + [str(i) for i in range(from_year, to_year + 1)]


def get_dimension(from_dim: float = 1, to_dim: float = 9, step: float = 0.1) -> list[str]:
    return [s_b] + [str(round(i, 1)) for i in np.arange(from_dim, to_dim + step, step)]


def get_cost(from_cost: int = 500, to_cost: int = 100000, step: int = 2500) -> list[str]:
    return [s_b] + [str(i) for i in range(from_cost, to_cost - step, step)]


# encode from strings = 'Citroen|C4|b|a|-|-|-|-|-|-' or list to full description
def decode_filter_short(string: str = None, lists: list = None, sep: str = '|'):
    motor_dict_reverse = dict(zip(motor_dict.values(), motor_dict.keys()))
    if lists is None:
        c = (string.split(sep=sep))
        if c[2] in motor_dict_reverse:
            c[2] = motor_dict_reverse[c[2]]
        if c[8] != s_b:
            c[8] = str(int(c[8]) / 1000)
        if c[9] != s_b:
            c[9] = str(int(c[9]) / 1000)
        if c[3] != s_b:
            c[3] = 'автомат' if c[3] == 'a' else 'механика'
    else:
        c = lists
    text = f"{c[0].replace(s_b, '<все бренды>')} {c[1].replace(s_b, '<все модели>')}\n" \
           f"{c[2].replace(s_b, '<все типы двигателей>')} {c[3].replace(s_b, '<все типы трансмиссий>')}\n" \
           f"с {c[4].replace(s_b, get_years()[1])}  по {c[5].replace(s_b, str(datetime.datetime.now().year))} г\n" \
           f"от {c[6].replace(s_b, get_cost()[1])}  до {c[7].replace(s_b, str(get_cost()[-1]))} $\n" \
           f"от {c[8].replace(s_b, get_dimension()[1])}  до {c[9].replace(s_b, str(get_dimension()[-1]))} л"
    return text if lists else text.replace('\n', ' | ')


# decode from lists of discription to 'filter=Citroen|C4|b|a|-|-|-|-|-|-'
def code_filter_short(cc: list = None):
    if cc[3] != s_b:
        cc[3] = 'a' if cc[3] == 'автомат' else 'm'
    if cc[2] in motor_dict:
        cc[2] = motor_dict[cc[2]]
    if cc[8] != s_b:
        cc[8] = str(int(cc[8].replace('.', '')) * 100)
    if cc[9] != s_b:
        cc[9] = str(int(cc[9].replace('.', '')) * 100)
    return 'filter=' + '|'.join(cc)


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
        await message.answer("Фильтр принят", reply_markup=ReplyKeyboardRemove())
        dicts = parse_av_by(car_link)
        if len(dicts) == 0:
            return await message.answer("По вашему запросу ничего не найдено,\n"
                                        "или запрашиваемый сервер перегружен")
        else:
            await message.reply(f"Найдено позиций - {len(dicts)}\nГотовим к отправке отчет")
            try:
                name_pdf_ = (str(datatime_datatime.now())).replace(':', s_b)
                try:
                    do_pdf(data=dicts,
                           name=name_pdf_,
                           filter_full=decode_filter_short(cars),
                           filter_short=message.text)
                except Exception as error:
                    print(str(error), "<--> Ошибка при формировании отчета")
                    return await message.answer("Ошибка при создании pdf")
                if os.path.exists(f'{name_pdf_}.pdf'):
                    file = FSInputFile(f'{name_pdf_}.pdf')
                    await bot.send_document(message.chat.id, document=file)
                    os.remove(f'{name_pdf_}.pdf')
                else:
                    print(f'{name_pdf_}.pdf не найден')
            except Exception as error:
                await message.answer(f"Не удалось отправить отчет,\n"
                                     f"поторите попытку позже")
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
    if len(c) > 0 and c[0] != s_b:
        await message.answer(
            text=decode_filter_short(lists=c),
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text='подтвердите фильтр:',
            reply_markup=multi_row_keyboard([code_filter_short(cc)])
        )
        await cooking_pdf(message=message)
    else:
        await message.answer(
            text=f"Фильтр пуст. Воспользуйтесь командой /car",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(Command(commands=["car"]))
@router.message(F.text.casefold() == "car")
async def brand_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_brand=s_b,
                            chosen_model=s_b,
                            chosen_motor=s_b,
                            chosen_transmission=s_b,
                            chosen_year_from=s_b,
                            chosen_year_to=s_b,
                            chosen_cost_min=s_b,
                            chosen_cost_max=s_b,
                            chosen_dimension_min=s_b,
                            chosen_dimension_max=s_b,
                            )
    await message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_keyboard(
            get_brands(),
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
            reply_markup=multi_row_keyboard(
                get_models(message.text),
                input_field_placeholder='имя модели')
            )
    else:
        await message.answer(
            text="Я не знаю такого бренда.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_brands(),
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
            reply_markup=multi_row_keyboard(
                motor,
                input_field_placeholder='тип топлива',
                columns=columns_motor,
            )
        )
    else:
        await message.answer(
            text="Я не знаю такой модели.\n"
                 "Пожалуйста, выберите один из вариантов из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_models(user_data['chosen_brand']),
                input_field_placeholder='имя модели'
            )
        )
        return motor_chosen
    await state.set_state(CreateCar.motor_choosing)


@router.message(CreateCar.motor_choosing)
async def transmission_chosen(message: Message, state: FSMContext):
    if message.text in motor:
        await state.update_data(chosen_motor=message.text)
        await message.answer(
            text="Теперь, выберите тип трансмиссии:",
            reply_markup=multi_row_keyboard(
                transmission,
                input_field_placeholder='тип трансмиссии'
            )
        )
    else:
        await message.answer(
            text="Я не знаю такого топлива.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                motor,
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
            reply_markup=multi_row_keyboard(
                get_years(),
                input_field_placeholder='год от',
                columns=columns_years,
            )
        )
    else:
        await message.answer(
            text="Я не знаю такой трансмиссии.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                transmission,
                input_field_placeholder='тип трансмиссии'
            )
        )
        return from_year_chosen
    await state.set_state(CreateCar.year_choosing)


@router.message(CreateCar.year_choosing)
async def to_year_chosen(message: Message, state: FSMContext):
    if message.text in get_years():
        year = get_years()[1] if message.text == s_b else message.text
        await state.update_data(chosen_year_from=message.text)
        await message.answer(
            text="Теперь, выберите по какой год:",
            reply_markup=multi_row_keyboard(
                get_years(from_year=int(year)),
                input_field_placeholder='год по',
                columns=columns_years,
            )
        )
    else:
        await message.answer(
            text="Год от введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_years(),
                input_field_placeholder='год от',
                columns=columns_years,
            )
        )
        return to_year_chosen
    await state.set_state(CreateCar.yearm_choosing)


@router.message(CreateCar.yearm_choosing)
async def min_cost_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    year = get_years()[1] if s_b == user_data['chosen_year_from'] else user_data['chosen_year_from']
    if message.text in get_years(from_year=int(year)):
        await state.update_data(chosen_year_to=message.text)
        await message.answer(
            text="Теперь, выберите начальную цену:",
            reply_markup=multi_row_keyboard(
                get_cost(),
                input_field_placeholder='стоимость от',
                columns=columns_cost,
            )
        )
    else:
        await message.answer(
            text="Год до введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_years(from_year=int(year)),
                input_field_placeholder='год по',
                columns=columns_years,
            )
        )
        return min_cost_chosen
    await state.set_state(CreateCar.cost_choosing)


@router.message(CreateCar.cost_choosing)
async def max_cost_chosen(message: Message, state: FSMContext):
    if message.text in get_cost():
        cost = get_cost()[1] if message.text == s_b else message.text
        await state.update_data(chosen_cost_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальную цену:",
            reply_markup=multi_row_keyboard(
                get_cost(from_cost=int(cost)),
                input_field_placeholder='стоимость до',
                columns=columns_cost,
            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_cost(),
                input_field_placeholder='стоимость от',
                columns=columns_cost,
            )
        )
        return max_cost_chosen
    await state.set_state(CreateCar.dimension_choosing)


@router.message(CreateCar.dimension_choosing)
async def min_dimension_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    cost = get_cost()[1] if s_b == user_data['chosen_cost_min'] else user_data['chosen_cost_min']
    if message.text in get_cost(from_cost=int(cost)):
        await state.update_data(chosen_cost_max=message.text)
        await message.answer(
            text="Теперь, выберите минимальный объем двигателя:",
            reply_markup=multi_row_keyboard(
                get_dimension(),
                input_field_placeholder='объем двигателя от',
                columns=columns_dimension,
            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_cost(from_cost=int(user_data['chosen_cost_min'])),
                input_field_placeholder='стоимость до',
                columns=columns_cost,
            )
        )
        return min_dimension_chosen
    await state.set_state(CreateCar.dimensionm_choosing)


@router.message(CreateCar.dimensionm_choosing)
async def max_dimension_chosen(message: Message, state: FSMContext):
    if message.text in get_dimension():
        dimension = get_dimension()[1] if message.text == s_b else message.text
        await state.update_data(chosen_dimension_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальный объем двигателя:",
            reply_markup=multi_row_keyboard(
                get_dimension(from_dim=float(dimension)),
                input_field_placeholder='объем двигателя до',
                columns=columns_dimension,
            )
        )
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_dimension(),
                input_field_placeholder='объем двигателя от',
                columns=columns_dimension,
            )
        )
        return max_dimension_chosen
    await state.set_state(CreateCar.finish_choosing)


@router.message(CreateCar.finish_choosing)
async def finish_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dimension = get_dimension()[1] if s_b == user_data['chosen_dimension_min'] \
        else user_data['chosen_dimension_min']
    if message.text in get_dimension(from_dim=float(dimension)):
        await state.update_data(chosen_dimension_max=message.text)
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_dimension(from_dim=float(user_data['chosen_dimension_min'])),
                input_field_placeholder='объем до',
            )
        )
        return finish_chosen
    await get_rusult(message=message, state=state)
