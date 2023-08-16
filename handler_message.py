from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from classes import CreateCar, bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards import multi_row_kb, result_menu_kb
from logic.database.config import database
from logic.func import get_years, get_cost, get_dimension, get_brands, get_models, decode_filter_short
from logic.constant import (FSB, CF, COL, MOTOR, TRANSMISSION, SB, EB, AV_ROOT, ABW_ROOT, DEFAULT)
from logic.text import TXT
from itertools import chain


router = Router()


@router.message(Command(commands=["build"]))
@router.message(Command(commands=["b"]))
@router.message((F.text.casefold() == "build") | (F.text.casefold() == "b") | (F.text == EB))
async def get_rusult(message: Message, state: FSMContext):
    await state.set_state(CreateCar.show_filter)
    data = await state.get_data()
    c = []
    [c.append(data[item].replace(SB, FSB)) for item in data]
    if len(c) > 0 and c[0] != FSB:
        await message.answer(
            text=TXT['msg_finish_filter'],
            reply_markup=result_menu_kb(fsm=c))
        await message.answer(
            text=TXT['msg_last_filter'].format(decode_filter_short=decode_filter_short(lists=c)),
            reply_markup=ReplyKeyboardRemove())
    else:
        await state.set_state(None)
        await message.answer(
            text=TXT['msg_empty_filter'],
            reply_markup=ReplyKeyboardRemove())


@router.message(Command(commands=["filter"]))
@router.message(Command(commands=["f"]))
@router.message((F.text.casefold() == "filter") | (F.text.casefold() == "f"))
@router.message(CreateCar.start_choosing)
async def brand_chosen(message: Message, state: FSMContext):
    await state.update_data(DEFAULT)
    await message.answer(
        text=TXT['f_brand'],
        reply_markup=multi_row_kb(await get_brands(), del_sb=True),
        input_field_placeholder=TXT['fi_brand'])
    await state.set_state(CreateCar.brand_choosing)


@router.message(CreateCar.brand_choosing)
async def model_chosen(message: Message, state: FSMContext):
    await message.delete()
    if message.text in await get_brands():
        await state.update_data(chosen_brand=message.text)
        await message.answer(
            text=TXT['f_model'],
            reply_markup=multi_row_kb(
                await get_models(message.text),
                input_field_placeholder=TXT['fi_model']))
    else:
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                await get_brands(),
                input_field_placeholder=TXT['fi_brand']))
        return model_chosen
    await state.set_state(CreateCar.model_choosing)


@router.message(CreateCar.model_choosing)
async def motor_chosen(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if message.text in await get_models(data['chosen_brand']) or message.text in CF:
        await state.update_data(chosen_model=message.text)
        await message.answer(
            text=TXT['f_motor'],
            reply_markup=multi_row_kb(
                MOTOR,
                input_field_placeholder=TXT['fi_motor'],
                columns=COL['MOTOR'],))
    else:
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                await get_models(data['chosen_brand']),
                input_field_placeholder=TXT['fi_model']))
        return motor_chosen
    await state.set_state(CreateCar.motor_choosing)


@router.message(CreateCar.motor_choosing)
async def transmission_chosen(message: Message, state: FSMContext):
    await message.delete()
    if message.text in chain(MOTOR, CF):
        await state.update_data(chosen_motor=message.text)
        await message.answer(
            text=TXT['f_transmission'],
            reply_markup=multi_row_kb(
                TRANSMISSION,
                input_field_placeholder=TXT['fi_transmission']))
    else:
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                MOTOR,
                input_field_placeholder=TXT['fi_motor'],
                columns=COL['MOTOR']))
        return transmission_chosen
    await state.set_state(CreateCar.transmission_choosing)


@router.message(CreateCar.transmission_choosing)
async def from_year_chosen(message: Message, state: FSMContext):
    await message.delete()
    if message.text in chain(TRANSMISSION, CF):
        data = await state.get_data()
        year = data['chosen_year_to']
        year = get_years()[-1] if year == SB else year
        await state.update_data(chosen_transmission=message.text)
        await message.answer(
            text=TXT['f_year_from'],
            reply_markup=multi_row_kb(
                get_years(to_year=int(year)),
                input_field_placeholder=TXT['fi_year_from'],
                columns=COL['YEARS']))
    else:
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                TRANSMISSION,
                input_field_placeholder=TXT['fi_transmission']))
        return from_year_chosen
    await state.set_state(CreateCar.year_choosing)


@router.message(CreateCar.year_choosing)
async def to_year_chosen(message: Message, state: FSMContext):
    await message.delete()
    year = get_years()[0] if message.text == SB else message.text
    if year in chain(list(get_years()), CF):
        await state.update_data(chosen_year_from=year)
        await message.answer(
            text=TXT['f_year_to'],
            reply_markup=multi_row_kb(
                get_years(from_year=int(year)),
                input_field_placeholder=TXT['fi_year_to'],
                columns=COL['YEARS']))
    else:
        data = await state.get_data()
        year = data['chosen_year_to']
        year = get_years()[-1] if year == SB else year
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                get_years(from_year=int(get_years()[0]), to_year=int(year)),
                input_field_placeholder=TXT['fi_year_from'],
                columns=COL['YEARS']))
        return to_year_chosen
    await state.set_state(CreateCar.yearm_choosing)


@router.message(CreateCar.yearm_choosing)
async def min_cost_chosen(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    year = data['chosen_year_from']
    year = get_years()[0] if SB == year else year
    if message.text in chain(get_years(from_year=int(year)), CF):
        await state.update_data(chosen_year_to=message.text)
        cost = data['chosen_cost_max']
        cost = get_cost()[-1] if cost == SB else cost
        await message.answer(
            text=TXT['f_price_from'],
            reply_markup=multi_row_kb(
                get_cost(to_cost=int(cost)),
                input_field_placeholder=TXT['fi_price_from'],
                columns=COL['COST']))
    else:
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                get_years(from_year=int(year)),
                input_field_placeholder=TXT['fi_year_to'],
                columns=COL['YEARS']))
        return min_cost_chosen
    await state.set_state(CreateCar.cost_choosing)


@router.message(CreateCar.cost_choosing)
async def max_cost_chosen(message: Message, state: FSMContext):
    await message.delete()
    if message.text in chain(get_cost(), CF):
        cost = get_cost()[0] if message.text == SB else message.text
        await state.update_data(chosen_cost_min=message.text)
        await message.answer(
            text=TXT['f_price_to'],
            reply_markup=multi_row_kb(
                get_cost(from_cost=int(cost)),
                input_field_placeholder=TXT['fi_price_to'],
                columns=COL['COST']))
    else:
        data = await state.get_data()
        cost = data['chosen_cost_max']
        cost = get_cost()[-1] if cost == SB else cost
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                get_cost(to_cost=int(cost)),
                input_field_placeholder=TXT['fi_price_from'],
                columns=COL['COST']))
        return max_cost_chosen
    await state.set_state(CreateCar.costm_choosing)


@router.message(CreateCar.costm_choosing)
async def min_dimension_chosen(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    cost = get_cost()[0] if SB == data['chosen_cost_min'] else data['chosen_cost_min']
    if message.text in chain(get_cost(from_cost=int(cost)), CF):
        await state.update_data(chosen_cost_max=message.text)
        dimension = data['chosen_dimension_max']
        dimension = get_dimension()[-1] if dimension == SB else dimension
        await message.answer(
            text=TXT['f_dimension_from'],
            reply_markup=multi_row_kb(
                get_dimension(to_dim=float(dimension)),
                input_field_placeholder=TXT['fi_dimension_from'],
                columns=COL['DIMENSION']))
    else:
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                get_cost(from_cost=int(data['chosen_cost_min'])),
                input_field_placeholder=TXT['fi_price_to'],
                columns=COL['COST']))
        return min_dimension_chosen
    await state.set_state(CreateCar.dimension_choosing)


@router.message(CreateCar.dimension_choosing)
async def max_dimension_chosen(message: Message, state: FSMContext):
    await message.delete()
    dimension = get_dimension()[0] if message.text == SB else message.text
    if dimension in chain(get_dimension(), CF):
        await state.update_data(chosen_dimension_min=dimension)
        await message.answer(
            text=TXT['fi_dimension_to'],
            reply_markup=multi_row_kb(
                get_dimension(from_dim=float(dimension)),
                input_field_placeholder=TXT['fi_dimension_to'],
                columns=COL['DIMENSION']))
    else:
        data = await state.get_data()
        dimension = data['chosen_dimension_max']
        dimension = get_dimension()[-1] if dimension == SB else dimension
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                get_dimension(to_dim=float(dimension)),
                input_field_placeholder=TXT['fi_dimension_from'],
                columns=COL['DIMENSION']))
        return max_dimension_chosen
    await state.set_state(CreateCar.dimensionm_choosing)


@router.message(CreateCar.dimensionm_choosing)
async def finish_chosen(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    dimension = data['chosen_dimension_min']
    dimension = get_dimension()[0] if SB == dimension else dimension
    if message.text in (get_dimension(from_dim=float(dimension)) + CF):
        await state.update_data(chosen_dimension_max=message.text)
    else:
        await message.answer(
            text=TXT['msg_error_filter_input'],
            reply_markup=multi_row_kb(
                get_dimension(from_dim=float(dimension)),
                input_field_placeholder=TXT['fi_dimension_to']))
        return finish_chosen
    await get_rusult(message=message, state=state)


@router.message(CreateCar.add_url_stalk)
async def add_stalk(message: Message):
    #  добавление ссылок через чат для отслеживания
    mes = message.text
    tel_id = message.from_user.id
    entities = message.entities or []
    await message.delete()
    for url in entities:
        if url.type == 'url':
            url = url.extract_from(mes)
            if url[:19] in (AV_ROOT + ABW_ROOT) and len(url.split('/')) >= 4:
                async with database() as db:
                    check_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = '{tel_id}'""")
                    check_id = await check_id_cursor.fetchone()
                    check_url_cursor = await db.execute(f"""SELECT url FROM ucars WHERE user_id = '{check_id[0]}'""")
                    check_url = await check_url_cursor.fetchall()
                    if url not in [i[0] for i in check_url]:
                        await db.execute(f"""INSERT INTO ucars (user_id, url, price)
                                             VALUES ('{check_id[0]}', '{url}', 0)""")
                        await db.commit()
                        await bot.send_message(
                            tel_id, TXT['msg_added_url'].format(url=url), disable_web_page_preview=True)
                    else:
                        await bot.send_message(
                            tel_id, TXT['msg_stalking_url'].format(url=url), disable_web_page_preview=True)
            else:
                await bot.send_message(tel_id, TXT['msg_error_url'], disable_web_page_preview=True)
