import os
from datetime import datetime as datatime_datatime
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from b_logic.get_url_cooking import all_get_url
from b_logic.parse_cooking import parse_main
from b_logic.pdf_cooking import do_pdf
from b_logic.func import get_count_cars, get_search_links, get_brands, decode_filter_short, code_filter_short
from b_logic.constant import s_b
from b_logic.database.config import database
from classes import CreateCar
from classes import bot
from keyboards import multi_row_keyboard, params_menu, start_menu_with_help, filter_menu


router = Router()


@router.callback_query(F.data == 'help_show_start_menu')
async def help_show_start_menu(callback: CallbackQuery):
    # показать помощь главном меню
    await callback.message.edit_text(
        'Этот бот сэкономит вам время в поиске подходящего автомобиля. '
        'Просто создайте и сохраните необходимый фильтр, и бот начнет вам присылать свежие обявления.\n'
        '- Открыть главное меню - /start.\n'
        '- Cоздать фильтр  - /car.\n'
        '- Если необходимо оставить параметр пустым выбирайте - [?].\n'
        '- Если хотите прпустить шаги с выбором параметров нажмите [menu]->[/show].\n'
        '- Сохраненные фильтры можно отключить или удалить в управлнии фильтрами.\n'
        '- Узнать больше команд /help.'
        , reply_markup=start_menu_with_help(False))


@router.callback_query(F.data == 'help_hide_start_menu')
async def help_hide_params_menu(callback: CallbackQuery):
    # скрыть помощь главном меню
    await callback.message.edit_text(
        'управление фильтрами',
        reply_markup=start_menu_with_help(True))


@router.callback_query(F.data == 'help_show_params_menu')
async def help_show_params_menu(callback: CallbackQuery):
    # отобразить помощь списка фильтров
    async with database() as db:
        await callback.message.edit_text(
            'Нажав на фильтр можно заказать сравнительный отчет о всех активных обявлениях.',
            reply_markup=await params_menu(decode_filter_short, callback, db, False))


@router.callback_query(F.data == 'help_hide_params_menu')
async def help_hide_params_menu(callback: CallbackQuery):
    # скрыть помощь списка фильтров
    async with database() as db:
        await callback.message.edit_text(
            'управление фильтрами',
            reply_markup=await params_menu(decode_filter_short, callback, db, True))



@router.callback_query(F.data == 'create_search')
async def brand_chosen(callback: CallbackQuery, state: FSMContext):
    # создать фильтр
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
    await callback.message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_keyboard(
            await get_brands(),
            input_field_placeholder='имя бренда',
            )
    )
    await state.set_state(CreateCar.brand_choosing)


@router.callback_query(F.data == 'cancel_start_menu')
async def cancel_start_menu(callback: CallbackQuery):
    # переход к главному меню
    await callback.message.edit_text('Главное меню', reply_markup=start_menu_with_help(True))


@router.callback_query(F.data == 'cancel_params_menu')
async def cancel_params_menu(callback: CallbackQuery):
    # переход к списку фильтров
    async with database() as db:
        await callback.message.edit_text('Список фильтров', reply_markup=await params_menu(decode_filter_short, callback, db, True))


@router.callback_query(F.data == 'save_search')
async def save_search(callback: CallbackQuery, state: FSMContext):
    # сохранение фильтра
    data = await state.get_data()
    c = []
    for item in data:
        c.append(data[item])
    car_code = code_filter_short(c)
    user_id = callback.from_user.id
    async with database() as db:
        check_id_cursor = await db.execute(f"SELECT tel_id FROM user WHERE tel_id = {user_id}")
        check_id = await check_id_cursor.fetchone()
        if check_id is None:
            await db.execute(f"INSERT INTO user (tel_id) VALUES ({user_id})")
        base_user_id_cursor = await db.execute(f"SELECT id FROM user WHERE tel_id = {user_id}")
        base_user_id = await base_user_id_cursor.fetchone()
        await db.executemany(
            f"INSERT INTO udata(user_id, search_param, is_active) "
            f"VALUES (?, ?, ?)", [(base_user_id[0], car_code, 1),]
        )
        await db.commit()
    await callback.message.edit_text('Теперь мы будем присылать вам лучшие объявления', reply_markup=start_menu_with_help(True))


@router.callback_query(F.data == 'show_search')
async def show_search(callback: CallbackQuery):
    # список фильтров
    async with database() as db:
        await callback.message.edit_text('Список фильтров', reply_markup=await params_menu(decode_filter_short, callback, db, True))


@router.callback_query((F.data.startswith('f_')) & (((F.data.endswith('_0')) | (F.data.endswith('_1')))))
async def edit_search(callback: CallbackQuery):
    # Включение/Отключение фильтров
     async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        user_id = check_id[0]
        params_id = callback.data.split('_')[2]        # {user.id}_{udata.id}_{udata.is_active}
        status_cursor = await db.execute(f"""SELECT is_active FROM udata 
                                             WHERE id='{params_id}' AND user_id = '{user_id}'""")
        status = await status_cursor.fetchone()
        status_set = 0 if status[0] == 1 else 1
        await db.execute(f"""UPDATE udata SET is_active = '{status_set}'                     
                             WHERE id='{params_id}' AND user_id = '{user_id}'
                        """)
        await db.commit()
        await callback.message.edit_text('Cписок фильтров', reply_markup=await params_menu(decode_filter_short, callback, db, True))


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_del')))
async def delete_search(callback: CallbackQuery):
    # Удаление фильтра
     async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        params_id = callback.data.split('_')[2]
        await db.execute(f"""DELETE FROM udata 
                             WHERE id='{params_id}' AND user_id = '{check_id[0]}'
                        """)
        await db.commit()
        await callback.message.edit_text('Список фильтров', reply_markup=await params_menu(decode_filter_short, callback, db, True))






@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_show')))
async def options_search(callback: CallbackQuery):
    # Опции фильтра, отображение кол-ва обявлений
    filter_id = callback.data.split('_')[1]
    async with database() as db:
        select_filter_cursor = await db.execute(f"""SELECT search_param FROM udata WHERE id = {filter_id}""")
        filter = await select_filter_cursor.fetchone()
    cars = filter[0][7:]

    av_link_json, abw_link_json, onliner_link_json = await all_get_url(cars, work=False)
    all_cars_av, all_cars_abw, all_cars_onliner = get_count_cars(av_link_json, abw_link_json, onliner_link_json)
    av_link, onliner_link, abw_link = get_search_links(cars, av_link_json, abw_link_json, onliner_link_json)


    all_count = [all_cars_av, all_cars_abw, all_cars_onliner]
    cars_count = sum(all_count)
    await callback.message.edit_text(
        f"{decode_filter_short(filter[0])[7:].replace('<', '').replace('>', '')}\n"
        f"\n"
        f"Найдено:\n"
        f"<a href='{av_link}'>av.by</a> - {all_cars_av}.\n"
        f"<a href='{abw_link}'>abw.by</a> - {all_cars_abw}.\n"
        f"<a href='{onliner_link}'>onliner.by</a> - {all_cars_onliner}.\n"
        f"\n"
        f"Действует ограничение до ~125 объявлений с 1 ресурса.\n",
        reply_markup=filter_menu(callback, cars_count),
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_rep')))
async def report_search(callback: CallbackQuery):
    # заказ отчета
    user_id = callback.from_user.id
    filter_id = callback.data.split('_')[1]
    async with database() as db:
        select_filter_cursor = await db.execute(f"""SELECT search_param FROM udata WHERE id = {filter_id}""")
        filter = await select_filter_cursor.fetchone()
    cars = filter[0][7:]

    av_link_json, abw_link_json, onliner_link_json = await all_get_url(cars, work=False)
    all_cars_av, all_cars_abw, all_cars_onliner = get_count_cars(av_link_json, abw_link_json, onliner_link_json)
    av_link, onliner_link, abw_link = get_search_links(cars, av_link_json, abw_link_json, onliner_link_json)

    name_time_stump = (str(datatime_datatime.now())).replace(':', '.')
    try:
        await parse_main(av_link_json,
                         abw_link_json,
                         onliner_link_json,
                         message=user_id,
                         name=name_time_stump,
                         work=False,
                         )
    except Exception as e:
        print(e, '\nОшибка в parse_main')
        return await bot.send_message(user_id,"Ошибка при сборе данных.\n"
                                    "Показать фильтр /show.")
    await bot.send_message(user_id, f"Сбор данных.")

    await do_pdf(
        message=user_id,
        link={
            'av': [av_link, all_cars_av],
            'abw': [abw_link, all_cars_abw],
            'onliner': [onliner_link, all_cars_onliner],
        },
        name=name_time_stump,
        filter_full=decode_filter_short(cars),
        filter_short=filter[0])
    os.remove(f'b_logic/buffer/{user_id}_{name_time_stump}.npy')

    if os.path.exists(f'b_logic/buffer/{name_time_stump}.pdf'):
        file = FSInputFile(f'b_logic/buffer/{name_time_stump}.pdf')
        await bot.send_document(user_id, document=file)
        os.remove(f'b_logic/buffer/{name_time_stump}.pdf')
    else:
        print(f'{name_time_stump}.pdf не найден')