from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards import back_to_start_menu_kb
from logic.database.config import database


router = Router()


@router.callback_query(F.data == 'admin')
async def admin(callback: CallbackQuery):

    async with database() as db:
        filters_cursor = await db.execute(
            """SELECT COUNT(udata.id) FROM udata"""
        )
        filters = await filters_cursor.fetchone()

    # админ меню
    text = f'{filters}бла бла'
    await callback.message.edit_text(text, reply_markup=back_to_start_menu_kb, parse_mode='HTML')
