import logging
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from classes import bot
from keyboards import params_menu_kb, filter_menu_kb
from logic.codec_filter import code_filter_short, decode_filter_short
from logic.constant import FSB, SB, REPORT_PARSE_LIMIT_PAGES
from logic.cook_parse_cars import parse_main
from logic.database.config import database
from logic.func import valid_params_filter_on_save, check_count_filters, check_count_filters_active, filter_import
from logic.text import TXT
from sites.sites_get_data import car_multidata
from work import send_pdf_job
from datetime import datetime as datatime_datatime


router = Router()


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
            user_id_cursor = await db.execute(f"SELECT id FROM user WHERE tel_id = '{tel_id}'")
            id_user = await user_id_cursor.fetchone()
            id_user = id_user[0]
            check_filter_cursor = await db.execute(f"SELECT search_param FROM udata WHERE user_id = '{id_user}'")
            check_filter = await check_filter_cursor.fetchall()

            if car_code not in [i[0] for i in check_filter]:

                status_is_active = await check_count_filters_active(tel_id)
                is_active = 1 if status_is_active else 0

                await db.executemany(
                    "INSERT INTO udata(user_id, search_param, is_active) "
                    "VALUES (?, ?, ?)", [(id_user, car_code, is_active), ])
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
            logging.info(f'<handler_callback_filters.edit_search> {e}')



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


@router.callback_query((F.data.endswith('_params_prev')) | (F.data.endswith('_params_next')))
async def pagination_params(callback: CallbackQuery):
    # список фильтров пагинация
    async with database() as db:
        page = int(callback.data.split('_')[0])
        await callback.message.edit_text(
            TXT['info_filter_menu'], reply_markup=await params_menu_kb(callback, db, True, page))


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
    json_links = multidata['json']
    html_links = multidata['link']
    cars_count = multidata['count']
    try:
        await parse_main(json=json_links, tel_id=tel_id, name=name_time_stump)
    except Exception as e:
        logging.error(f'<handler_callback.report_search.parse_main> {e}')

        return await bot.send_message(tel_id, TXT['msg_error'])
    async with database() as db:
        await callback.message.edit_text(TXT['info_filter_menu'],
                                         reply_markup=await params_menu_kb(callback, db, True),
                                         disable_web_page_preview=True,
                                         parse_mode="HTML", )
    link_count = dict(link=html_links, count=cars_count)
    await bot.send_message(tel_id, TXT['msg_cooking_rep'])
    await send_pdf_job(tel_id, link_count, name_time_stump, decode_filter_short(cars), filter_name)
