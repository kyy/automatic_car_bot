from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards import start_menu_kb, back_to_start_menu_kb, car_message_details_kb, delete_message_kb

from logic.func import strip_html
from logic.text import TXT
from logic.constant import BOT

from sites.sites_get_data import get_car_details

router = Router()


@router.callback_query(F.data.startswith('start_menu_help'))
async def help_show_start_menu(callback: CallbackQuery):
    #   показать/скрыть помощь главном меню
    cd = callback.data.split('_')
    text_false = TXT['info_start_menu_help']
    text_true = TXT['info_start_menu']
    help_flag, text = (False, text_false) if cd[3] == 'show' else (True, text_true)
    await callback.message.edit_text(text, reply_markup=await start_menu_kb(help_flag, callback), parse_mode='HTML')


@router.callback_query(F.data == 'bot_functions')
async def bot_functions(callback: CallbackQuery):
    #   описание бота

    await callback.message.edit_text(
        text=TXT['info_bot'].format(telegram=BOT['telegram'], telegram_name=BOT['telegram_name'], email=BOT['email']),
        reply_markup=back_to_start_menu_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@router.callback_query(F.data == 'message_delete')
async def message_delete(callback: CallbackQuery):
    #   удалить сообщение
    await callback.message.delete()


@router.callback_query(F.data.endswith('_research'))
async def car_details(callback: CallbackQuery):
    # отображение дополнительной информации о машине
    data = callback.data.split('_')
    url, is_price = data[0], data[1]

    url = f'https://{url}'

    params = await get_car_details(url)

    kb = delete_message_kb() if is_price == 'price' else car_message_details_kb()
    text = params if params else f'{callback.message.caption}\n Не удалось ничего узнать'

    await callback.message.edit_caption(
        caption=strip_html(text),
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=kb,
    )
