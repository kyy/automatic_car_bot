import logging
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from bot_config import CreateCar, bot
from keyboards import stalk_menu_kb, add_stalk_kb
from logic.constant import ROOT_URL
from logic.database.config import database
from logic.func import check_count_cars, check_count_cars_active
from logic.text import TXT
from sites.sites_get_data import get_br_mod_pr

router = Router()


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


@router.callback_query((F.data.startswith('s_')) & ((F.data.endswith('_0')) | (F.data.endswith('_1'))))
async def edit_stalk(callback: CallbackQuery):
    # включение/отключение слежки
    tel_id = callback.from_user.id
    async with database() as db:
        select_id_cursor = await db.execute("""SELECT id FROM user WHERE tel_id=$s""", (tel_id,))
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
            await db.execute("""UPDATE ucars SET is_active=$status_set                     
                                WHERE id=$params_id AND user_id=$user_id""", (status_set, params_id, user_id,))
            message = TXT['info_stalk_menu']
            await db.commit()
        try:
            await callback.message.edit_text(
                message,
                reply_markup=await stalk_menu_kb(callback, db, True, page))
        except Exception as e:
            logging.info(f"<handler_callback_price_tracking.edit_stalk> {e}")


@router.callback_query(F.data == 'car_follow')
async def car_follow(callback: CallbackQuery):
    #   добавить в слежку из рассылки
    tel_id = callback.from_user.id

    status_add_limit = await check_count_cars(tel_id, bot)
    status_is_active = await check_count_cars_active(tel_id)
    if status_add_limit:
        message = callback.message.caption.split('\n')

        url, price = message[0], int(message[1][1:])

        async with database() as db:

            check_id_cursor = await db.execute("""SELECT id FROM user WHERE tel_id=$s""", (tel_id,))
            check_id = await check_id_cursor.fetchone()

            check_url_cursor = await db.execute("""SELECT url FROM ucars WHERE user_id=$s""", (check_id[0],))
            check_url = await check_url_cursor.fetchall()

            if message[0] not in [i[0] for i in check_url]:
                is_active = 1 if status_is_active else 0
                name, current_price = await get_br_mod_pr(url)
                price = current_price if current_price != 0 else price
                await db.execute("""INSERT INTO ucars (user_id, url, price, is_active, name) 
                                     VALUES (?, ?, ?, ?, ?)""", (check_id[0], url, price, is_active, name))
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


@router.callback_query((F.data.startswith('s_')) & (F.data.endswith('_del')))
async def delete_stulk(callback: CallbackQuery):
    # удаление из слежки
    async with database() as db:
        tel_id = callback.from_user.id
        select_id_cursor = await db.execute("""SELECT id FROM user WHERE tel_id = $s""", (tel_id,))
        check_id = await select_id_cursor.fetchone()
        cd = callback.data.split('_')
        params_id = cd[1]
        page = int(cd[2])
        await db.execute("""DELETE FROM ucars WHERE id=$params_id AND user_id=$check_id""", (params_id, check_id[0],))
        await db.commit()
        await callback.message.edit_text(
            TXT['info_stalk_menu'], reply_markup=await stalk_menu_kb(callback, db, True, page))


@router.callback_query(F.data == 'add_stalk')
async def add_stalk_from_message(callback: CallbackQuery, state: FSMContext):
    # добавление слежки вручную
    await state.set_state(CreateCar.add_url_stalk)
    await callback.message.edit_text(
        TXT['info_add_stalk_menu'], reply_markup=add_stalk_kb)


@router.message(CreateCar.add_url_stalk)
async def add_stalk(message: Message):
    #  добавление ссылок через чат для отслеживания
    mes = message.text
    tel_id = message.from_user.id
    entities = message.entities or []
    await message.delete()
    status_add_limit = await check_count_cars(tel_id, bot)
    if status_add_limit:
        for url in entities:
            if url.type == 'url':
                url = url.extract_from(mes)
                url_valid = f"{'/'.join(url.split('/')[:3])}/"
                if url_valid in [''.join(i) for i in ROOT_URL.values()] and len(url.split('/')) >= 4:
                    async with database() as db:

                        check_id_cursor = await db.execute("""SELECT id FROM user WHERE tel_id=$s""",
                                                           (tel_id,))
                        check_id = await check_id_cursor.fetchone()

                        check_url_cursor = await db.execute("""SELECT url FROM ucars WHERE user_id=$s""",
                                                            (check_id[0],))
                        check_url = await check_url_cursor.fetchall()

                        if url not in [i[0] for i in check_url]:
                            status_is_active = await check_count_cars_active(tel_id)
                            is_active = 1 if status_is_active else 0

                            name, price = await get_br_mod_pr(url)

                            await db.execute("""INSERT INTO ucars (user_id, url, price, is_active, name)
                                                 VALUES (?, ?, ?, ?, ?)""", (check_id[0], url, price, is_active, name))

                            await db.commit()
                            await bot.send_message(
                                tel_id, TXT['msg_added_url'].format(url=url), disable_web_page_preview=True)
                        else:
                            await bot.send_message(
                                tel_id, TXT['msg_stalking_url'].format(url=url), disable_web_page_preview=True)
                else:
                    await bot.send_message(tel_id, TXT['msg_error_url'], disable_web_page_preview=True)
