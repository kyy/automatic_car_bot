from datetime import datetime as datatime_datatime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from classes import CreateCar
from classes import bot
from keyboards import (multi_row_kb, params_menu_kb, start_menu_kb, filter_menu_kb, bot_functions_kb, stalk_menu_kb,
                       add_stalk_kb)
from logic.constant import (FSB, SB, MOTOR, TRANSMISSION, COL, DEFAULT, MM, REPORT_PARSE_LIMIT_PAGES)
from logic.cook_parse_cars import parse_main
from logic.database.config import database
from logic.func import (get_brands, decode_filter_short, code_filter_short, car_multidata, filter_import, get_models,
                        get_years, get_cost, get_dimension, valid_params_filter_on_save, check_count_filters,
                        check_count_filters_active, check_count_cars, check_count_cars_active)
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


@router.callback_query(F.data == 'save_search')
async def save_search(callback: CallbackQuery, state: FSMContext):
    #   сохранение фильтра
    tel_id = callback.from_user.id
    data = await state.get_data()

    status_valid_params_filter_on_save = await valid_params_filter_on_save(tel_id, data, bot)
    status_check_count_filters = await check_count_filters(tel_id, bot)

    if status_valid_params_filter_on_save and status_check_count_filters:

        c = []
        [c.append(data[item].replace(SB, FSB)) for item in data]
        car_code = code_filter_short(c)

        async with database() as db:
            check_id_cursor = await db.execute(f"SELECT tel_id FROM user WHERE tel_id = '{tel_id}'")
            check_id = await check_id_cursor.fetchone()
            if check_id is None:
                await db.execute(f"INSERT INTO user (tel_id) VALUES ('{tel_id}')")
            user_id_cursor = await db.execute(f"SELECT id FROM user WHERE tel_id = '{tel_id}'")
            id_user = await user_id_cursor.fetchone()
            check_filter_cursor = await db.execute(f"SELECT search_param FROM udata WHERE user_id = '{id_user[0]}'")
            check_filter = await check_filter_cursor.fetchall()

            if car_code not in [i[0] for i in check_filter]:

                status_is_active = await check_count_filters_active(tel_id)
                is_active = 1 if status_is_active else 0

                await db.executemany(
                    "INSERT INTO udata(user_id, search_param, is_active) "
                    "VALUES (?, ?, ?)", [(id_user[0], car_code, is_active), ])
                await db.commit()
                await state.set_state(None)
                await callback.message.edit_text(
                    TXT['info_save_search'],
                    reply_markup=await params_menu_kb(callback, db, help_flag=True))
            else:
                await bot.send_message(tel_id, TXT['msg_dublicate_filter'])


@router.callback_query(F.data == 'show_search')
async def show_search(callback: CallbackQuery):
    #   список фильтров
    async with database() as db:
        await callback.message.edit_text(
            TXT['info_filter_menu'], reply_markup=await params_menu_kb(callback, db, True))


@router.callback_query((F.data.startswith('f_')) & ((F.data.endswith('_0')) | (F.data.endswith('_1'))))
async def edit_search(callback: CallbackQuery):
    # включение/отключение фильтров
    async with database() as db:
        tel_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {tel_id}""")
        check_id = await select_id_cursor.fetchone()
        user_id = check_id[0]

        cd = callback.data.split('_')

        params_id = cd[1]
        page = int(cd[2])
        status_car_active = (cd[3])
        is_active = int(cd[4])

        status_set = 0 if is_active == 1 else 1
        message = TXT['msg_limit']
        if status_car_active == 'True' or status_car_active == 'False' and is_active == 1:
            await db.execute(f"""UPDATE udata SET is_active = '{status_set}'                     
                                 WHERE id='{params_id}' AND user_id = '{user_id}'""")
            message = TXT['info_filter_menu']
            await db.commit()
        try:
            await callback.message.edit_text(
                message,
                reply_markup=await params_menu_kb(callback, db, True, page))
        except Exception as e:
            print(e, '[handler_callback.edit_search]')


@router.callback_query((F.data.startswith('s_')) & ((F.data.endswith('_0')) | (F.data.endswith('_1'))))
async def edit_stalk(callback: CallbackQuery):
    # включение/отключение слежки
    tel_id = callback.from_user.id
    async with database() as db:
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {tel_id}""")
        check_id = await select_id_cursor.fetchone()
        user_id = check_id[0]

        cd = callback.data.split('_')

        params_id = cd[1]
        page = int(cd[2])
        status_car_active = (cd[3])
        is_active = int(cd[4])

        status_set = 0 if is_active == 1 else 1
        message = TXT['msg_limit']
        if status_car_active == 'True' or status_car_active == 'False' and is_active == 1:
            await db.execute(f"""UPDATE ucars SET is_active = '{status_set}'                     
                                     WHERE id='{params_id}' AND user_id = '{user_id}'""")
            message = TXT['info_stalk_menu']
            await db.commit()
        try:
            await callback.message.edit_text(
                message,
                reply_markup=await stalk_menu_kb(callback, db, True, page))
        except Exception as e:
            print(e, '[handler_callback.edit_stalk]')


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
    multidata = await car_multidata(cars)
    count = multidata['count']
    link = multidata['link']
    cars_count = sum([int(i) for i in count.values()])
    await callback.message.edit_text(
        text=TXT['info_filter'].format(
            decode_filter_short=decode_filter_short(cars),
            av_l=link['av_link'],
            all_av=count['all_av'],
            abw_l=link['abw_link'],
            all_abw=count['all_abw'],
            onliner_l=link['onliner_link'],
            all_onliner=count['all_onliner'],
            kufar_l=link['kufar_link'],
            all_kufar=count['all_kufar'],
            size=25 * REPORT_PARSE_LIMIT_PAGES),
        reply_markup=filter_menu_kb(callback, cars_count),
        disable_web_page_preview=True,
        parse_mode="HTML")


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_rep')))
async def report_search(callback: CallbackQuery):
    #   заказ отчета
    tel_id = callback.from_user.id
    filter_id, filter_name, cars = await filter_import(callback, database())
    multidata = await car_multidata(cars)
    name_time_stump = (str(datatime_datatime.now())).replace(':', '.')
    try:
        await parse_main(multidata['json'], tel_id=tel_id, name=name_time_stump)
    except Exception as e:
        print(e, 'handler_control_callback.report_search.parse_main')
        return await bot.send_message(tel_id, TXT['msg_error'])
    async with database() as db:
        await callback.message.edit_text(TXT['info_filter_menu'],
                                         reply_markup=await params_menu_kb(callback, db, True),
                                         disable_web_page_preview=True,
                                         parse_mode="HTML", )
    link_count = dict(link=multidata['link'], count=multidata['count'])
    await bot.send_message(tel_id, TXT['msg_cooking_rep'])
    await send_pdf_job(tel_id, link_count, name_time_stump, decode_filter_short(cars), filter_name)


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
    #   Добавить в слежку из рассылки
    tel_id = callback.from_user.id

    status_add_limit = await check_count_cars(tel_id, bot)
    status_is_active = await check_count_cars_active(tel_id)
    if status_add_limit:
        message = callback.message.text.split('\n')
        async with database() as db:

            check_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = '{tel_id}'""")
            check_id = await check_id_cursor.fetchone()

            check_url_cursor = await db.execute(f"""SELECT url FROM ucars WHERE user_id = '{check_id[0]}'""")
            check_url = await check_url_cursor.fetchall()

            if message[0] not in [i[0] for i in check_url]:
                is_active = 1 if status_is_active else 0

                await db.execute(f"""INSERT INTO ucars (user_id, url, price, is_active) 
                                     VALUES (?, ?, ?, ?)""", (check_id[0], message[0], int(message[1][1:]), is_active))
                await db.commit()
            await callback.message.delete()


@router.callback_query(F.data == 'show_stalk')
async def car_stalk(callback: CallbackQuery):
    # список слежки
    async with database() as db:
        await callback.message.edit_text(
            TXT['info_stalk_menu'], reply_markup=await stalk_menu_kb(callback, db, True))


@router.callback_query((F.data.endswith('_stalk_prev')) | (F.data.endswith('_stalk_next')))
async def pagination_stalk(callback: CallbackQuery):
    # список слежки пагинация
    async with database() as db:
        page = int(callback.data.split('_')[0])
        await callback.message.edit_text(
            TXT['info_stalk_menu'], reply_markup=await stalk_menu_kb(callback, db, True, page))


@router.callback_query((F.data.endswith('_params_prev')) | (F.data.endswith('_params_next')))
async def pagination_params(callback: CallbackQuery):
    # список фильтров пагинация
    async with database() as db:
        page = int(callback.data.split('_')[0])
        await callback.message.edit_text(
            TXT['info_filter_menu'], reply_markup=await params_menu_kb(callback, db, True, page))


@router.callback_query((F.data.startswith('s_')) & (F.data.endswith('_del')))
async def delete_stulk(callback: CallbackQuery):
    # удаление из слежки
    async with database() as db:
        tel_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {tel_id}""")
        check_id = await select_id_cursor.fetchone()
        cd = callback.data.split('_')
        params_id = cd[1]
        page = int(cd[2])
        await db.execute(f"""DELETE FROM ucars
                             WHERE id='{params_id}' AND user_id = '{check_id[0]}'""")
        await db.commit()
        await callback.message.edit_text(
            TXT['info_stalk_menu'], reply_markup=await stalk_menu_kb(callback, db, True, page))


@router.callback_query(F.data == 'add_stalk')
async def add_stulk_from_message(callback: CallbackQuery, state: FSMContext):
    # добавление слежки вручную
    await state.set_state(CreateCar.add_url_stalk)
    await callback.message.edit_text(
        TXT['info_add_stalk_menu'], reply_markup=add_stalk_kb)


@router.callback_query(F.data == 'create_search')
async def brand_chosen(callback: CallbackQuery, state: FSMContext):
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
