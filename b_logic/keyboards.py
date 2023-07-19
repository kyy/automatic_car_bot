from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def single_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def multi_row_keyboard(items: list[str], columns: int = 4, **kwargs) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(*[KeyboardButton(text=item) for item in items]).adjust(columns)
    return builder.as_markup(**kwargs)


def start_menu_with_help(help):
    help_callback = 'help_show_start_menu' if help is True else 'help_hide_start_menu'
    buttons = [
        [
            InlineKeyboardButton(text="📝 Создать фильтр", callback_data="create_search"),
            InlineKeyboardButton(text="🖼 Управление фильтрами", callback_data="show_search")
        ],
        [
            InlineKeyboardButton(text="🔎 Помощь", callback_data=help_callback)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)




result_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Сохранить фильтр", callback_data="save_search"),
            InlineKeyboardButton(text="🖼 Отмена", callback_data="cancel_start_menu")
        ],
        [
            InlineKeyboardButton(text="🔎 Помощь", callback_data="help_show_start_menu")
        ]
    ])


async def params_menu(decode_filter_short, callback, db):
    """
    Клавиатура управления фильтрами
    :param decode_filter_short:
    :param callback:
    :param db:
    :return:
    """
    user_id = callback.from_user.id
    search_params_cursor = await db.execute(f"SELECT udata.search_param, udata.is_active, udata.id FROM user "
                                            f"INNER JOIN udata on user.id = udata.user_id "
                                            f"WHERE user.tel_id = {user_id}")
    search_params = await search_params_cursor.fetchall()
    buttons = [
            [InlineKeyboardButton(text=decode_filter_short(i[0])[7:], callback_data=f'f={user_id}_{i[2]}_show'),
            InlineKeyboardButton(text=str(i[1]).replace('1', 'Отключить').replace('0', 'Активировать'), callback_data=f'f={user_id}_{i[2]}_{i[1]}'),
            InlineKeyboardButton(text='Удалить', callback_data=f'f={user_id}_{i[2]}_del'),
             ] for i in search_params]
    buttons.append([InlineKeyboardButton(text='назад', callback_data='cancel_start_menu'),
                    InlineKeyboardButton(text='🔎 Помощь', callback_data='help_show_params_menu')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
