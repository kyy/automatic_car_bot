from datetime import datetime as datatime_datatime
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from logic.cook_parse_cars import parse_main
from logic.func import (get_brands, decode_filter_short, code_filter_short, car_multidata, filter_import, get_models,
                        get_years, get_cost, get_dimension)
from logic.constant import FSB, SB, MOTOR, COL_MOTOR, TRANSMISSION, COL_YEARS, COL_COST, COL_DIMENSION, default
from logic.database.config import database
from classes import CreateCar
from classes import bot
from keyboards import (multi_row_kb, params_menu_kb, start_menu_kb, filter_menu_kb, bot_functions_kb, stalk_menu_kb,
                       add_stalk_kb)
from logic.text import TXT
from work import send_pdf_job


router = Router()


@router.callback_query(F.data.startswith('start_menu_help'))
async def help_show_start_menu(callback: CallbackQuery):
    #   показать/скрыть помощь главном меню
    cd = callback.data.split('_')
    text_false = TXT['info_start_menu_help']
    text_true = TXT['info_start_menu']
    help_flag, text = (False, text_false) if cd[3] == 'show' else (True, text_true)
    await callback.message.edit_text(text, reply_markup=start_menu_kb(help_flag), parse_mode='HTML')


@router.callback_query(F.data.startswith('params_menu_help'))
async def help_show_params_menu(callback: CallbackQuery):
    #   показать/скрыть  помощь списка фильтров
    async with database() as db:
        cd = callback.data.split('_')
        page = int(cd[4])
        text_false = TXT['info_filter_menu_help']
        text_true = TXT['info_filter_menu']
        help_flag, text = (False, text_false) if cd[3] == 'show' else (True, text_true)
        await callback.message.edit_text(text, reply_markup=await params_menu_kb(callback, db, help_flag, page))


@router.callback_query(F.data.startswith('stalk_menu_help'))
async def help_show_stalk_menu(callback: CallbackQuery):
    #   показать/скрыть помощь слежки меню
    async with database() as db:
        cd = callback.data.split('_')
        page = int(cd[4])
        text_false = TXT['info_stalk_menu_help']
        text_true = TXT['info_stalk_menu']
        help_flag, text = (False, text_false) if cd[3] == 'show' else (True, text_true)
        await callback.message.edit_text(text, reply_markup=await stalk_menu_kb(callback, db, help_flag, page))


@router.callback_query(F.data == 'create_search')
async def brand_chosen(callback: CallbackQuery, state: FSMContext):
    #   создать фильтр
    await state.update_data(default)
    await callback.message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_kb(await get_brands(), del_sb=True),
        input_field_placeholder='имя бренда',
        )
    await state.set_state(CreateCar.brand_choosing)


@router.callback_query(F.data == 'save_search')
async def save_search(callback: CallbackQuery, state: FSMContext):
    #   сохранение фильтра
    data = await state.get_data()
    c = []
    for item in data:
        c.append(data[item].replace(SB, FSB))
    car_code = code_filter_short(c)
    user_id = callback.from_user.id
    async with database() as db:
        check_id_cursor = await db.execute(f"SELECT tel_id FROM user WHERE tel_id = '{user_id}'")
        check_id = await check_id_cursor.fetchone()
        if check_id is None:
            await db.execute(f"INSERT INTO user (tel_id) VALUES ('{user_id}')")
        user_id_cursor = await db.execute(f"SELECT id FROM user WHERE tel_id = '{user_id}'")
        user_id = await user_id_cursor.fetchone()
        check_filter_cursor = await db.execute(f"SELECT search_param FROM udata WHERE user_id = '{user_id[0]}'")
        check_filter = await check_filter_cursor.fetchall()
        if car_code not in [i[0] for i in check_filter]:
            await db.executemany(
                f"INSERT INTO udata(user_id, search_param, is_active) "
                f"VALUES (?, ?, ?)", [(user_id[0], car_code, 1), ])
            await db.commit()
        await callback.message.edit_text(
            TXT['info_save_search'],
            reply_markup=await params_menu_kb(callback, db, help_flag=True))


@router.callback_query(F.data == 'show_search')
async def show_search(callback: CallbackQuery):
    #   список фильтров
    async with database() as db:
        await callback.message.edit_text(
            TXT['info_filter_menu'],
            reply_markup=await params_menu_kb(callback, db, True))


@router.callback_query((F.data.startswith('f_')) & ((F.data.endswith('_0')) | (F.data.endswith('_1'))))
async def edit_search(callback: CallbackQuery):
    # включение/отключение фильтров
    async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        user_id = check_id[0]
        cd = callback.data.split('_')
        params_id = cd[1]
        page = int(cd[2])
        status_cursor = await db.execute(f"""SELECT is_active FROM udata 
                                             WHERE id='{params_id}' AND user_id = '{user_id}'""")
        status = await status_cursor.fetchone()
        status_set = 0 if status[0] == 1 else 1
        await db.execute(f"""UPDATE udata SET is_active = '{status_set}'                     
                             WHERE id='{params_id}' AND user_id = '{user_id}'""")
        await db.commit()
        await callback.message.edit_text(
            TXT['info_filter_menu'],
            reply_markup=await params_menu_kb(callback, db, True, page))


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_del')))
async def delete_search(callback: CallbackQuery):
    #   удаление фильтра
    async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        cd = callback.data.split('_')
        params_id = cd[1]
        page = int(cd[2])
        await db.execute(f"""DELETE FROM udata 
                             WHERE id='{params_id}' AND user_id = '{check_id[0]}'""")
        await db.commit()
        await callback.message.edit_text(
            TXT['info_filter_menu'],
            reply_markup=await params_menu_kb(callback, db, True, page))


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_show')))
async def options_search(callback: CallbackQuery):
    #   опции фильтра, отображение кол-ва объявлений
    filter_id, filter_name, cars = await filter_import(callback, database())
    av_jsn, abw_jsn, onliner_jsn, all_av, all_abw, all_onliner, av_l, abw_l, onliner_l = await car_multidata(cars)
    all_count = [all_av, all_abw, all_onliner]
    cars_count = sum(all_count)
    await callback.message.edit_text(
        text=TXT['info_filter'].format(
            decode_filter_short=decode_filter_short(filter_name[0][7:]),
            av_l=av_l,
            all_av=all_av,
            abw_l=abw_l,
            all_abw=all_abw,
            onliner_l=onliner_l,
            all_onliner=all_onliner),
        reply_markup=filter_menu_kb(callback, cars_count),
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_rep')))
async def report_search(callback: CallbackQuery):
    #   заказ отчета
    user_id = callback.from_user.id
    filter_id, filter_name, cars = await filter_import(callback, database())
    av_jsn, abw_jsn, onliner_jsn, all_av, all_abw, all_onliner, av_l, abw_l, onliner_l = await car_multidata(cars)
    name_time_stump = (str(datatime_datatime.now())).replace(':', '.')
    try:
        await parse_main(av_jsn, abw_jsn, onliner_jsn, user_id, name_time_stump)
    except Exception as e:
        print(e, 'Ошибка в parse_main')
        return await bot.send_message(user_id, TXT['msg_error'])
    async with database() as db:
        await callback.message.edit_text(TXT['msg_collect_data'],
                                         reply_markup=await params_menu_kb(callback, db, True),
                                         disable_web_page_preview=True,
                                         parse_mode="HTML", )
    link_count = {'av': [av_l, all_av],
                  'abw': [abw_l, all_abw],
                  'onliner': [onliner_l, all_onliner]}
    await bot.send_message(user_id, TXT['msg_cooking_rep'])
    await send_pdf_job(user_id, link_count, name_time_stump, decode_filter_short(cars), filter_name[0])


@router.callback_query(F.data == 'bot_functions')
async def bot_functions(callback: CallbackQuery):
    #   описание бота
    await callback.message.edit_text(TXT['info_bot'],
                                     reply_markup=bot_functions_kb,
                                     disable_web_page_preview=True,
                                     parse_mode="HTML", )


@router.callback_query(F.data == 'message_delete')
async def message_delete(callback: CallbackQuery):
    #   удалить сообщение
    await callback.message.delete()


@router.callback_query(F.data == 'car_follow')
async def car_follow(callback: CallbackQuery):
    #   Добавить в слежку
    tel_id = callback.from_user.id
    message = callback.message.text.split('\n')
    async with database() as db:
        check_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = '{tel_id}'""")
        check_id = await check_id_cursor.fetchone()
        check_url_cursor = await db.execute(f"""SELECT url FROM ucars WHERE user_id = '{check_id[0]}'""")
        check_url = await check_url_cursor.fetchall()
        if message[0] not in [i[0] for i in check_url]:
            await db.execute(f"""INSERT INTO ucars (user_id, url, price) 
                                 VALUES ('{check_id[0]}', '{message[0]}', '{int(message[1][1:])}')""")
            await db.commit()
        await bot.delete_message(
            chat_id=tel_id,
            message_id=callback.message.message_id)


@router.callback_query(F.data == 'show_stalk')
async def car_stalk(callback: CallbackQuery):
    # список слежки
    async with database() as db:
        await callback.message.edit_text(
            TXT['info_stalk_menu'],
            reply_markup=await stalk_menu_kb(callback, db, True))


@router.callback_query((F.data.endswith('_stalk_prev')) | (F.data.endswith('_stalk_next')))
async def pagination_stalk(callback: CallbackQuery):
    # список слежки пагинация
    async with database() as db:
        page = int(callback.data.split('_')[0])
        await callback.message.edit_text(
            TXT['info_stalk_menu'],
            reply_markup=await stalk_menu_kb(callback, db, True, page))


@router.callback_query((F.data.endswith('_params_prev')) | (F.data.endswith('_params_next')))
async def pagination_params(callback: CallbackQuery):
    # список фильтров пагинация
    async with database() as db:
        page = int(callback.data.split('_')[0])
        await callback.message.edit_text(
            TXT['info_filter_menu'],
            reply_markup=await params_menu_kb(callback, db, True, page))


@router.callback_query((F.data.startswith('s_')) & (F.data.endswith('_del')))
async def delete_search(callback: CallbackQuery):
    # удаление из слежки
    async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        cd = callback.data.split('_')
        params_id = cd[1]
        page = int(cd[2])
        await db.execute(f"""DELETE FROM ucars
                             WHERE id='{params_id}' AND user_id = '{check_id[0]}'""")
        await db.commit()
        await callback.message.edit_text(
            TXT['info_stalk_menu'],
            reply_markup=await stalk_menu_kb(callback, db, True, page))


@router.callback_query(F.data == 'add_stalk')
async def delete_search(callback: CallbackQuery, state: FSMContext):
    # добавление слежки вручную
    await state.set_state(CreateCar.add_url_stalk)
    await callback.message.edit_text(
        TXT['info_add_stalk_menu'],
        reply_markup=add_stalk_kb)


@router.callback_query(F.data == 'edit_search')
async def brand_chosen(callback: CallbackQuery, state: FSMContext):
    # создать фильтр
    await state.update_data(chosen_model=SB)  # сбрасываем модель при смене бренда
    await callback.message.answer(
        text=TXT['f_brand'],
        reply_markup=multi_row_kb(await get_brands(), del_sb=True),
        input_field_placeholder=TXT['fi_brand'],
        )
    await state.set_state(CreateCar.brand_choosing)


@router.callback_query(F.data == 'cb_model')
async def edit_model(callback: CallbackQuery, state: FSMContext):
    # изменить модель
    data = await state.get_data()
    brand = data['chosen_brand']
    await callback.message.answer(
            text=TXT['f_model'],
            reply_markup=multi_row_kb(
                await get_models(brand),
                input_field_placeholder=TXT['fi_model'])
            )
    await state.set_state(CreateCar.model_choosing)


@router.callback_query(F.data == 'cb_motor')
async def edit_motor(callback: CallbackQuery, state: FSMContext):
    # изменить двигатель
    await callback.message.answer(
            text=TXT['f_motor'],
            reply_markup=multi_row_kb(
                MOTOR,
                input_field_placeholder=TXT['fi_motor'],
                columns=COL_MOTOR,
            )
        )
    await state.set_state(CreateCar.motor_choosing)


@router.callback_query(F.data == 'cb_transmission')
async def edit_transmission(callback: CallbackQuery, state: FSMContext):
    # изменить двигатель
    await callback.message.answer(
            text=TXT['f_transmission'],
            reply_markup=multi_row_kb(
                TRANSMISSION,
                input_field_placeholder=TXT['fi_transmission']
            )
        )
    await state.set_state(CreateCar.transmission_choosing)


@router.callback_query(F.data == 'cb_year_from')
async def edit_year_from(callback: CallbackQuery, state: FSMContext):
    # изменить год от
    data = await state.get_data()
    year = data['chosen_year_to']
    year = get_years()[-1] if year == SB else year
    await callback.message.answer(
            text=TXT['f_year_from'],
            reply_markup=multi_row_kb(
                get_years(to_year=int(year)),
                input_field_placeholder=TXT['fi_year_from'],
                columns=COL_YEARS,
            )
        )
    await state.set_state(CreateCar.year_choosing)


@router.callback_query(F.data == 'cb_year_to')
async def edit_year_to(callback: CallbackQuery, state: FSMContext):
    # изменить го до
    data = await state.get_data()
    year = data['chosen_year_from']
    if year == SB:
        year = get_years()[1]
    await callback.message.answer(
            text=TXT['f_year_to'],
            reply_markup=multi_row_kb(
                get_years(from_year=int(year)),
                input_field_placeholder=TXT['fi_year_to'],
                columns=COL_YEARS,
            )
        )
    await state.set_state(CreateCar.yearm_choosing)


@router.callback_query(F.data == 'cb_price_from')
async def edit_price_from(callback: CallbackQuery, state: FSMContext):
    # изменить цена от
    data = await state.get_data()
    cost = data['chosen_cost_max']
    cost = get_cost()[-1] if cost == SB else cost
    await callback.message.answer(
            text=TXT['f_price_from'],
            reply_markup=multi_row_kb(
                get_cost(to_cost=int(cost)),
                input_field_placeholder=TXT['fi_price_from'],
                columns=COL_COST,
            )
        )
    await state.set_state(CreateCar.cost_choosing)


@router.callback_query(F.data == 'cb_price_to')
async def edit_price_to(callback: CallbackQuery, state: FSMContext):
    # изменить цена до
    data = await state.get_data()
    cost = data['chosen_cost_min']
    if cost == SB:
        cost = get_cost()[0]
    await callback.message.answer(
            text=TXT['f_price_to'],
            reply_markup=multi_row_kb(
                get_cost(from_cost=int(cost)),
                input_field_placeholder=TXT['fi_price_to'],
                columns=COL_COST,
            )
        )
    await state.set_state(CreateCar.costm_choosing)


@router.callback_query(F.data == 'cb_dimension_from')
async def edit_dimension_from(callback: CallbackQuery, state: FSMContext):
    # изменить объем от
    data = await state.get_data()
    dimension = data['chosen_dimension_max']
    dimension = get_dimension()[-1] if dimension == SB else dimension
    await callback.message.answer(
            text=TXT['f_dimension_from'],
            reply_markup=multi_row_kb(
                get_dimension(to_dim=float(dimension)),
                input_field_placeholder=TXT['f_dimension_from'],
                columns=COL_DIMENSION,
            )
        )
    await state.set_state(CreateCar.dimension_choosing)


@router.callback_query(F.data == 'cb_dimension_to')
async def edit_dimension_to(callback: CallbackQuery, state: FSMContext):
    # изменить объем до
    data = await state.get_data()
    dimension = data['chosen_dimension_min']
    if dimension == SB:
        dimension = get_dimension()[0]
    await callback.message.answer(
            text=TXT['f_dimension_to'],
            reply_markup=multi_row_kb(
                get_dimension(from_dim=float(dimension)),
                input_field_placeholder=TXT['f_dimension_to'],
                columns=COL_DIMENSION,
            )
        )
    await state.set_state(CreateCar.dimensionm_choosing)
