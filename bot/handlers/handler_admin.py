from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards import back_to_start_menu_kb

from logic.database.config import database

router = Router()


@router.callback_query(F.data == 'admin')
async def admin(callback: CallbackQuery):
    async with database() as db:
        filters_cursor = await db.execute(
            """SELECT COUNT(udata.id) FROM udata"""
        )
        filters = await filters_cursor.fetchone()

        stalks_cursor = await db.execute(
            """SELECT COUNT(ucars.id) FROM ucars"""
        )
        stalks = await stalks_cursor.fetchone()

        users_cursor = await db.execute(
            """SELECT COUNT(user.id) FROM user"""
        )
        users = await users_cursor.fetchone()

    # админ меню
    text = f'фильтров: {filters[0]}\n' \
           f'машин: {stalks[0]}\n' \
           f'пользователей: {users[0]}\n'
    await callback.message.edit_text(text, reply_markup=back_to_start_menu_kb, parse_mode='HTML')
