from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards import start_menu_kb, bot_functions_kb, car_message_details_kb, delete_message_kb
from logic.func import strip_html
from logic.text import TXT
from sites.sites_get_data import get_car_details

router = Router()


@router.callback_query(F.data.startswith('start_menu_help'))
async def help_show_start_menu(callback: CallbackQuery):
    #   показать/скрыть помощь главном меню
    cd = callback.data.split('_')
    text_false = TXT['info_start_menu_help']
    text_true = TXT['info_start_menu']
    help_flag, text = (False, text_false) if cd[3] == 'show' else (True, text_true)
    await callback.message.edit_text(text, reply_markup=start_menu_kb(help_flag), parse_mode='HTML')


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


@router.callback_query(F.data.endswith('_research'))
async def car_details(callback: CallbackQuery):
    # отображение дополнительной информации о машине
    data = callback.data.split('_')
    domen, car_id, is_price = data[0], data[1], data[2]

    params = await get_car_details(car_id, domen)

    kb = delete_message_kb() if is_price == 'price' else car_message_details_kb()
    text = params if params else f'{callback.message.caption}\n Не удалось ничего узнать'



    await callback.message.edit_caption(
        caption=strip_html(text),
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=kb,
    )
