from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from classes import CreateCar
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards import multi_row_kb, result_menu_kb
from logic.func import get_years, get_cost, get_dimension, get_brands, get_models, decode_filter_short
from logic.constant import SB, COL_COST, COL_YEARS, COL_DIMENSION, COL_MOTOR, MOTOR, TRANSMISSION


router = Router()


@router.message(Command(commands=["show"]))
@router.message(F.text.casefold() == "show")
async def get_rusult(message: Message, state: FSMContext):
    await state.set_state('finish_choosing')
    data = await state.get_data()
    c = []
    for item in data:
        c.append(data[item])

    if len(c) > 0 and c[0] != SB:
        await message.answer(
            text=decode_filter_short(lists=c),
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text='Управление фильтром:',
            reply_markup=result_menu_kb,
        )
    else:
        await message.answer(
            text=f"Фильтр пуст. Воспользуйтесь командой /car",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(Command(commands=["car"]))
@router.message(F.text.casefold() == "car")
async def brand_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_brand=SB,
                            chosen_model=SB,
                            chosen_motor=SB,
                            chosen_transmission=SB,
                            chosen_year_from=SB,
                            chosen_year_to=SB,
                            chosen_cost_min=SB,
                            chosen_cost_max=SB,
                            chosen_dimension_min=SB,
                            chosen_dimension_max=SB,
                            )
    await message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_kb(
            await get_brands(),
            input_field_placeholder='имя бренда',
            )
    )
    await state.set_state(CreateCar.brand_choosing)


@router.message(CreateCar.brand_choosing)
async def model_chosen(message: Message, state: FSMContext):
    if message.text in await get_brands():
        await state.update_data(chosen_brand=message.text)
        await message.answer(
            text="Теперь, выберите модель:",
            reply_markup=multi_row_kb(
                await get_models(message.text),
                input_field_placeholder='имя модели')
            )

    else:
        await message.answer(
            text="Я не знаю такого бренда.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                await get_brands(),
                input_field_placeholder='имя бренда')
        )
        return model_chosen
    await state.set_state(CreateCar.model_choosing)


@router.message(CreateCar.model_choosing)
async def motor_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in await get_models(user_data['chosen_brand']):
        await state.update_data(chosen_model=message.text)
        await message.answer(
            text="Теперь, выберите тип топлива:",
            reply_markup=multi_row_kb(
                MOTOR,
                input_field_placeholder='тип топлива',
                columns=COL_MOTOR,
            )
        )
    else:
        await message.answer(
            text="Я не знаю такой модели.\n"
                 "Пожалуйста, выберите один из вариантов из списка ниже:",
            reply_markup=multi_row_kb(
                await get_models(user_data['chosen_brand']),
                input_field_placeholder='имя модели'
            )
        )
        return motor_chosen

    await state.set_state(CreateCar.motor_choosing)


@router.message(CreateCar.motor_choosing)
async def transmission_chosen(message: Message, state: FSMContext):
    if message.text in MOTOR:
        await state.update_data(chosen_motor=message.text)
        await message.answer(
            text="Теперь, выберите тип трансмиссии:",
            reply_markup=multi_row_kb(
                TRANSMISSION,
                input_field_placeholder='тип трансмиссии'
            )
        )
    else:
        await message.answer(
            text="Я не знаю такого топлива.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                MOTOR,
                input_field_placeholder='тип топлива',
                columns=COL_MOTOR,
            )
        )
        return transmission_chosen
    await state.set_state(CreateCar.transmission_choosing)


@router.message(CreateCar.transmission_choosing)
async def from_year_chosen(message: Message, state: FSMContext):
    if message.text in TRANSMISSION:
        await state.update_data(chosen_transmission=message.text)
        await message.answer(
            text="Теперь, выберите с какого года:",
            reply_markup=multi_row_kb(
                get_years(),
                input_field_placeholder='год от',
                columns=COL_YEARS,
            )
        )
    else:
        await message.answer(
            text="Я не знаю такой трансмиссии.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                TRANSMISSION,
                input_field_placeholder='тип трансмиссии'
            )
        )
        return from_year_chosen
    await state.set_state(CreateCar.year_choosing)


@router.message(CreateCar.year_choosing)
async def to_year_chosen(message: Message, state: FSMContext):
    if message.text in get_years():
        year = get_years()[1] if message.text == SB else message.text
        await state.update_data(chosen_year_from=message.text)
        await message.answer(
            text="Теперь, выберите по какой год:",
            reply_markup=multi_row_kb(
                get_years(from_year=int(year)),
                input_field_placeholder='год по',
                columns=COL_YEARS,
            )
        )
    else:
        await message.answer(
            text="Год от введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                get_years(),
                input_field_placeholder='год от',
                columns=COL_YEARS,
            )
        )
        return to_year_chosen
    await state.set_state(CreateCar.yearm_choosing)


@router.message(CreateCar.yearm_choosing)
async def min_cost_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    year = get_years()[1] if SB == user_data['chosen_year_from'] else user_data['chosen_year_from']
    if message.text in get_years(from_year=int(year)):
        await state.update_data(chosen_year_to=message.text)
        await message.answer(
            text="Теперь, выберите начальную цену:",
            reply_markup=multi_row_kb(
                get_cost(),
                input_field_placeholder='стоимость от',
                columns=COL_COST,
            )
        )
    else:
        await message.answer(
            text="Год до введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                get_years(from_year=int(year)),
                input_field_placeholder='год по',
                columns=COL_YEARS,
            )
        )
        return min_cost_chosen
    await state.set_state(CreateCar.cost_choosing)


@router.message(CreateCar.cost_choosing)
async def max_cost_chosen(message: Message, state: FSMContext):
    if message.text in get_cost():
        cost = get_cost()[1] if message.text == SB else message.text
        await state.update_data(chosen_cost_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальную цену:",
            reply_markup=multi_row_kb(
                get_cost(from_cost=int(cost)),
                input_field_placeholder='стоимость до',
                columns=COL_COST,
            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                get_cost(),
                input_field_placeholder='стоимость от',
                columns=COL_COST,
            )
        )
        return max_cost_chosen
    await state.set_state(CreateCar.dimension_choosing)


@router.message(CreateCar.dimension_choosing)
async def min_dimension_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    cost = get_cost()[1] if SB == user_data['chosen_cost_min'] else user_data['chosen_cost_min']
    if message.text in get_cost(from_cost=int(cost)):
        await state.update_data(chosen_cost_max=message.text)
        await message.answer(
            text="Теперь, выберите минимальный объем двигателя:",
            reply_markup=multi_row_kb(
                get_dimension(),
                input_field_placeholder='объем двигателя от',
                columns=COL_DIMENSION,
            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                get_cost(from_cost=int(user_data['chosen_cost_min'])),
                input_field_placeholder='стоимость до',
                columns=COL_COST,
            )
        )
        return min_dimension_chosen
    await state.set_state(CreateCar.dimensionm_choosing)


@router.message(CreateCar.dimensionm_choosing)
async def max_dimension_chosen(message: Message, state: FSMContext):
    if message.text in get_dimension():
        dimension = get_dimension()[1] if message.text == SB else message.text
        await state.update_data(chosen_dimension_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальный объем двигателя:",
            reply_markup=multi_row_kb(
                get_dimension(from_dim=float(dimension)),
                input_field_placeholder='объем двигателя до',
                columns=COL_DIMENSION,
            )
        )
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                get_dimension(),
                input_field_placeholder='объем двигателя от',
                columns=COL_DIMENSION,
            )
        )
        return max_dimension_chosen
    await state.set_state(CreateCar.finish_choosing)


@router.message(CreateCar.finish_choosing)
async def finish_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dimension = get_dimension()[1] if SB == user_data['chosen_dimension_min'] \
        else user_data['chosen_dimension_min']
    if message.text in get_dimension(from_dim=float(dimension)):
        await state.update_data(chosen_dimension_max=message.text)
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_kb(
                get_dimension(from_dim=float(user_data['chosen_dimension_min'])),
                input_field_placeholder='объем до',
            )
        )
        return finish_chosen
    await get_rusult(message=message, state=state)
