from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.states import CreateCar
from bot.keyboards import multi_row_kb

from logic.constant import SB, MOTOR, TRANSMISSION, COL, DEFAULT, MM
from logic.kb_fu import get_brands, get_models, get_years, get_cost, get_dimension
from logic.text import TXT

router = Router()


@router.callback_query(F.data == 'create_search')
async def create_filter(callback: CallbackQuery, state: FSMContext):
    #   создать фильтр
    await state.update_data(DEFAULT)
    await callback.message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_kb(await get_brands(), del_sb=True),
        input_field_placeholder='имя бренда',
    )
    await state.set_state(CreateCar.brand_choosing)


@router.callback_query(F.data == 'edit_search')
async def brand_chosen(callback: CallbackQuery, state: FSMContext):
    # изменить бренд
    await callback.message.delete()
    await state.update_data(chosen_model=SB)  # сбрасываем модель при смене бренда
    await callback.message.answer(
        text=TXT['f_brand'],
        reply_markup=multi_row_kb(await get_brands(), del_sb=True),
        input_field_placeholder=TXT['fi_brand'])
    await state.set_state(CreateCar.brand_choosing)


@router.callback_query(F.data == 'cb_model')
async def edit_model(callback: CallbackQuery, state: FSMContext):
    # изменить модель
    await callback.message.delete()
    data = await state.get_data()
    brand = data['chosen_brand']
    await callback.message.answer(
        text=TXT['f_model'],
        reply_markup=multi_row_kb(
            await get_models(brand),
            input_field_placeholder=TXT['fi_model']))
    await state.set_state(CreateCar.model_choosing)


@router.callback_query(F.data == 'cb_motor')
async def edit_motor(callback: CallbackQuery, state: FSMContext):
    # изменить двигатель
    await callback.message.delete()
    await callback.message.answer(
        text=TXT['f_motor'],
        reply_markup=multi_row_kb(
            MOTOR,
            input_field_placeholder=TXT['fi_motor'],
            columns=COL['MOTOR']))
    await state.set_state(CreateCar.motor_choosing)


@router.callback_query(F.data == 'cb_transmission')
async def edit_transmission(callback: CallbackQuery, state: FSMContext):
    # изменить двигатель
    await callback.message.delete()
    await callback.message.answer(
        text=TXT['f_transmission'],
        reply_markup=multi_row_kb(
            TRANSMISSION,
            input_field_placeholder=TXT['fi_transmission']))
    await state.set_state(CreateCar.transmission_choosing)


@router.callback_query(F.data == 'cb_year_from')
async def edit_year_from(callback: CallbackQuery, state: FSMContext):
    # изменить год от
    await callback.message.delete()
    data = await state.get_data()
    year = data['chosen_year_to']
    year = get_years()[-1] if year == SB else year
    await callback.message.answer(
        text=TXT['f_year_from'],
        reply_markup=multi_row_kb(
            get_years(to_year=int(year)),
            input_field_placeholder=TXT['fi_year_from'],
            columns=COL['YEARS']))
    await state.set_state(CreateCar.year_choosing)


@router.callback_query(F.data == 'cb_year_to')
async def edit_year_to(callback: CallbackQuery, state: FSMContext):
    # изменить год до
    await callback.message.delete()
    data = await state.get_data()
    year = data['chosen_year_from']
    year = get_years()[1] if year == SB else year
    await callback.message.answer(
        text=TXT['f_year_to'],
        reply_markup=multi_row_kb(
            get_years(from_year=int(year)),
            input_field_placeholder=TXT['fi_year_to'],
            columns=COL['YEARS']))
    await state.set_state(CreateCar.yearm_choosing)


@router.callback_query(F.data == 'cb_price_from')
async def edit_price_from(callback: CallbackQuery, state: FSMContext):
    # изменить цена от
    await callback.message.delete()
    data = await state.get_data()
    cost = data['chosen_cost_max']
    cost = get_cost()[-1] if cost == SB else cost
    await callback.message.answer(
        text=TXT['f_price_from'],
        reply_markup=multi_row_kb(
            get_cost(to_cost=int(cost)),
            input_field_placeholder=TXT['fi_price_from'],
            columns=COL['COST']))
    await state.set_state(CreateCar.cost_choosing)


@router.callback_query(F.data == 'cb_price_to')
async def edit_price_to(callback: CallbackQuery, state: FSMContext):
    # изменить цена до
    await callback.message.delete()
    data = await state.get_data()
    cost = data['chosen_cost_min']
    cost = get_cost()[0] if cost == SB else cost
    await callback.message.answer(
        text=TXT['f_price_to'],
        reply_markup=multi_row_kb(
            get_cost(from_cost=int(cost) + MM['STEP_COST']),
            input_field_placeholder=TXT['fi_price_to'],
            columns=COL['COST']))
    await state.set_state(CreateCar.costm_choosing)


@router.callback_query(F.data == 'cb_dimension_from')
async def edit_dimension_from(callback: CallbackQuery, state: FSMContext):
    # изменить объем от
    await callback.message.delete()
    data = await state.get_data()
    dimension = data['chosen_dimension_max']
    dimension = get_dimension()[-1] if dimension == SB else dimension
    await callback.message.answer(
        text=TXT['f_dimension_from'],
        reply_markup=multi_row_kb(
            get_dimension(to_dim=float(dimension)),
            input_field_placeholder=TXT['f_dimension_from'],
            columns=COL['DIMENSION']))
    await state.set_state(CreateCar.dimension_choosing)


@router.callback_query(F.data == 'cb_dimension_to')
async def edit_dimension_to(callback: CallbackQuery, state: FSMContext):
    # изменить объем до
    await callback.message.delete()
    data = await state.get_data()
    dimension = data['chosen_dimension_min']
    if dimension == SB:
        dimension = get_dimension()[0]
    await callback.message.answer(
        text=TXT['f_dimension_to'],
        reply_markup=multi_row_kb(
            get_dimension(from_dim=float(dimension)),
            input_field_placeholdrer=TXT['f_dimension_to'],
            columns=COL['DIMENSION']))
    await state.set_state(CreateCar.dimensionm_choosing)
