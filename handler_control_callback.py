import asyncio
from datetime import datetime as datatime_datatime
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from logic.cook_parse import parse_main
from logic.func import get_brands, decode_filter_short, code_filter_short, car_multidata, filter_import
from logic.constant import SB
from logic.database.config import database
from classes import CreateCar
from classes import bot
from keyboards import multi_row_kb, params_menu_kb, start_menu_kb, filter_menu_kb, bot_functions_kb, stalk_menu_kb
from work import send_pdf_job


router = Router()


@router.callback_query(F.data == 'start_menu_help_show')
async def help_show_start_menu(callback: CallbackQuery):
    # показать помощь главном меню
    await callback.message.edit_text(
        'БОТ поможет вам найти подходящий автомобиль. '
        'Просто создайте и сохраните необходимый поиск-фильтр, и БОТ начнет вам присылать свежие обявления.\n'
        '- Открыть главное меню - /start.\n'
        '- Cоздать фильтр  - /car.\n'
        '- Если необходимо оставить параметр пустым выбирайте - [?].\n'
        '- Если хотите прпустить шаги с выбором параметров нажмите [menu]->[/show].\n'
        '- Сохраненные фильтры можно отключить или удалить в управлнии фильтрами.\n'
        '- Узнать больше команд /help.',
        reply_markup=start_menu_kb(False))


@router.callback_query(F.data == 'start_menu_help_hide')
async def help_hide_params_menu(callback: CallbackQuery):
    # скрыть помощь главном меню
    await callback.message.edit_text(
        'Главное меню',
        reply_markup=start_menu_kb(True))


@router.callback_query(F.data == 'params_menu_help_show')
async def help_show_params_menu(callback: CallbackQuery):
    # отобразить помощь списка фильтров
    async with database() as db:
        await callback.message.edit_text(
            'Нажав на фильтр можно заказать сравнительный отчет о всех активных объявлениях.\n'
            'Отчет представляет собой PDF-файл, нажав на марку в файле можно перейти к обявлению на сайте.',
            'Отчет содержит, VIN, сколько дней опубликовано объявление, город... и многое другое.',
            reply_markup=await params_menu_kb(callback, db, False))


@router.callback_query(F.data == 'params_menu_help_hide')
async def help_hide_params_menu(callback: CallbackQuery):
    # скрыть помощь списка фильтров
    async with database() as db:
        await callback.message.edit_text(
            'Список фильтров',
            reply_markup=await params_menu_kb(callback, db, True))


@router.callback_query(F.data == 'stalk_menu_help_show')
async def help_show_stalk_menu(callback: CallbackQuery):
    # показать помощь слежки меню
    async with database() as db:
        await callback.message.edit_text(
            'БОТ уведомит вас о изменениях цен на машины в этом списке. ',
            reply_markup=await stalk_menu_kb(callback, db, False))


@router.callback_query(F.data == 'stalk_menu_help_hide')
async def help_hide_stalk_menu(callback: CallbackQuery):
    # скрыть помощь слежки меню
    async with database() as db:
        await callback.message.edit_text(
            'Список слежки',
            reply_markup=await stalk_menu_kb(callback, db, True))


@router.callback_query(F.data == 'create_search')
async def brand_chosen(callback: CallbackQuery, state: FSMContext):
    # создать фильтр
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
    await callback.message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_kb(
            await get_brands(),
            input_field_placeholder='имя бренда',
        )
    )
    await state.set_state(CreateCar.brand_choosing)


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
        'Теперь мы будем присылать вам свежие объявления\n'
        'Узнать все текущие объявления можно сформировав отчет в управлении фильтрами.\n'
        'При возникновении трудноситей жми [Помощь].\n',
        reply_markup=await params_menu_kb(callback, db, help_flag=True))


@router.callback_query(F.data == 'show_search')
async def show_search(callback: CallbackQuery):
    # список фильтров
    async with database() as db:
        await callback.message.edit_text(
            'Список фильтров',
            reply_markup=await params_menu_kb(callback, db, True))


@router.callback_query((F.data.startswith('f_')) & ((F.data.endswith('_0')) | (F.data.endswith('_1'))))
async def edit_search(callback: CallbackQuery):
    # включение/отключение фильтров
    async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        user_id = check_id[0]
        params_id = callback.data.split('_')[1]  #{udata.id}_{udata.is_active}
        status_cursor = await db.execute(f"""SELECT is_active FROM udata 
                                             WHERE id='{params_id}' AND user_id = '{user_id}'""")
        status = await status_cursor.fetchone()
        status_set = 0 if status[0] == 1 else 1
        await db.execute(f"""UPDATE udata SET is_active = '{status_set}'                     
                             WHERE id='{params_id}' AND user_id = '{user_id}'""")
        await db.commit()
        await callback.message.edit_text(
            'Cписок фильтров',
            reply_markup=await params_menu_kb(callback, db, True))


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_del')))
async def delete_search(callback: CallbackQuery):
    # удаление фильтра
    async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        params_id = callback.data.split('_')[1]
        await db.execute(f"""DELETE FROM udata 
                             WHERE id='{params_id}' AND user_id = '{check_id[0]}'""")
        await db.commit()
        await callback.message.edit_text(
            'Список фильтров',
            reply_markup=await params_menu_kb(callback, db, True))


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_show')))
async def options_search(callback: CallbackQuery):
    # опции фильтра, отображение кол-ва объявлений
    filter_id, filter_name, cars = await filter_import(callback, database())
    av_jsn, abw_jsn, onliner_jsn, all_av, all_abw, all_onliner, av_l, abw_l, onliner_l = await car_multidata(cars)
    all_count = [all_av, all_abw, all_onliner]
    cars_count = sum(all_count)
    await callback.message.edit_text(
        f"{decode_filter_short(filter_name[0])[7:].replace('<', '').replace('>', '')}\n"
        f"\n"
        f"Найдено:\n"
        f"<a href='{av_l}'>av.by</a> - {all_av}.\n"
        f"<a href='{abw_l}'>abw.by</a> - {all_abw}.\n"
        f"<a href='{onliner_l}'>onliner.by</a> - {all_onliner}.\n"
        f"\n"
        f"Действует ограничение до ~125 объявлений с 1 ресурса.\n",
        reply_markup=filter_menu_kb(callback, cars_count),
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@router.callback_query((F.data.startswith('f_')) & (F.data.endswith('_rep')))
async def report_search(callback: CallbackQuery):
    # заказ отчета
    user_id = callback.from_user.id
    filter_id, filter_name, cars = await filter_import(callback, database())
    av_jsn, abw_jsn, onliner_jsn, all_av, all_abw, all_onliner, av_l, abw_l, onliner_l = await car_multidata(cars)
    name_time_stump = (str(datatime_datatime.now())).replace(':', '.')
    try:
        await parse_main(av_jsn, abw_jsn, onliner_jsn, user_id, name_time_stump)
    except Exception as e:
        print(e, 'Ошибка в parse_main')
        return await bot.send_message(user_id, "Ошибка при сборе данных.\n")
    async with database() as db:
        await callback.message.edit_text("Сбор данных.",
                                         reply_markup=await params_menu_kb(callback, db),
                                         disable_web_page_preview=True,
                                         parse_mode="HTML", )
    link_count = {'av': [av_l, all_av],
                  'abw': [abw_l, all_abw],
                  'onliner': [onliner_l, all_onliner]}
    await bot.send_message(user_id, 'готовим отчет')
    await send_pdf_job(user_id, link_count, name_time_stump, decode_filter_short(cars), filter_name[0])


@router.callback_query(F.data == 'bot_functions')
async def bot_functions(callback: CallbackQuery):
    #   описание бота
    await callback.message.edit_text(
        "Основные функции:\n"
        "- Автоматическая рассылка пользователям свежих обявлений. "
        "Управление рассылками.\n"
        "- Удобный отчет с текущими обявлениями в формате PDF. "
        "Отчет содержит данные, доступ к котором ограничен на сайтах.\n"
        "Пожеланния, вопросы:\nTelegram  <a href='https://t.me/Xibolba'>@Xibolba</a>\ne-mail  insider_2012@mail.ru\n",
         reply_markup=bot_functions_kb,
         disable_web_page_preview=True,
         parse_mode="HTML", )


@router.callback_query(F.data == 'message_delete')
async def message_delete(callback: CallbackQuery):
    # удалить сообщение
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id, )


@router.callback_query(F.data == 'car_follow')
async def car_follow(callback: CallbackQuery):
    # Добавить в слежку
    tel_id =callback.from_user.id
    message = callback.message.text.split('$')
    async with database() as db:
        check_id_cursor = await db.execute(f"SELECT id FROM user WHERE tel_id = '{tel_id}'")
        check_id = await check_id_cursor.fetchone()
        check_url_cursor = await db.execute(f"SELECT url FROM ucars WHERE user_id = '{check_id[0]}'")
        check_url = await check_url_cursor.fetchall()
        if message not in [i[0] for i in check_url]:
            await db.execute(f"INSERT INTO ucars (user_id, url, price) VALUES ('{check_id[0]}', '{message[0]}', '{int(message[1])}')")
            await db.commit()
            await callback.message.edit_text(
                "Добавлено",
                 disable_web_page_preview=True,
                 parse_mode="HTML", )
        await asyncio.sleep(4)
        await bot.delete_message(
            chat_id=tel_id,
            message_id=callback.message.message_id)


@router.callback_query(F.data == 'show_stalk')
async def car_stalk(callback: CallbackQuery):
    # список слежки
    async with database() as db:
        await callback.message.edit_text(
            'Список слежки',
            reply_markup=await stalk_menu_kb(callback, db, True))


@router.callback_query((F.data.startswith('s_')) & (F.data.endswith('_del')))
async def delete_search(callback: CallbackQuery):
    # удаление из слежки
    async with database() as db:
        user_id = callback.from_user.id
        select_id_cursor = await db.execute(f"""SELECT id FROM user WHERE tel_id = {user_id}""")
        check_id = await select_id_cursor.fetchone()
        params_id = callback.data.split('_')[1]
        await db.execute(f"""DELETE FROM ucars
                             WHERE id='{params_id}' AND user_id = '{check_id[0]}'""")
        await db.commit()
        await callback.message.edit_text(
            'Список слежки',
            reply_markup=await stalk_menu_kb(callback, db, True))
