from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from keyboards import start_menu_kb, bot_functions_kb, car_message_details_kb, delete_message_kb
from logic.constant import LOGO
from logic.func import strip_html
from sites.av.av_parse_json import av_research
from sites.kufar.kufar_parse_json import kufar_research
from sites.onliner.onliner_parse_json import onliner_research
from logic.text import TXT


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
    # отображение дополнительной информации
    data = callback.data.split('_')
    domen, car_id, is_price = data[0], data[1], data[2]

    params = False, False

    if 'av.by' in domen:
        params = av_research(car_id)
    elif 'onliner.by' in domen:
        params = onliner_research(car_id)
    elif 'kufar.by' in domen:
        params = kufar_research(car_id)
    elif 'abw.by' in domen:
        pass

    kb = delete_message_kb() if is_price == 'price' else car_message_details_kb()
    text = params[0] if params[0] else f'{callback.message.caption}\n Не удалось ничего узнать'
    photo = FSInputFile(LOGO) if params[1] == '' else params[1]

    await callback.message.edit_caption(
        photo=photo,
        caption=strip_html(text),
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=kb,
    )
