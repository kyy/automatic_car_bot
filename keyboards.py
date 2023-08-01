from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardBuilder
from logic.func import decode_filter_short


def single_row_kb(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def multi_row_kb(items: list[str], columns: int = 4, **kwargs) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(*[KeyboardButton(text=item) for item in items]).adjust(columns)
    return builder.as_markup(**kwargs)


def start_menu_kb(help_flag):
    # главное меню
    help_callback = 'start_menu_help_show' if help_flag is True else 'start_menu_help_hide'
    help_text = "🔎 Помощь" if help_flag is True else "🔎 Скрыть помощь"
    buttons = [[
        InlineKeyboardButton(
            text="🖼 Бот",
            callback_data="bot_functions"),
        InlineKeyboardButton(
            text="🖼 Поиск",
            callback_data="show_search"),
        InlineKeyboardButton(
            text="🖼 Слежка",
            callback_data="show_stalk")], [
        InlineKeyboardButton(
            text=help_text,
            callback_data=help_callback)]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_menu_kb():
    # меню сформированного фильтра
    buttons = [[
        InlineKeyboardButton(
            text="📝 Сохранить фильтр",
            callback_data="save_search"),
        InlineKeyboardButton(
            text="🖼 Отмена",
            callback_data="start_menu_help_hide")]]
    state_class = [('1','1'), ('2','1'), ('3','1'), ('4','1'), ('5','1'), ('6','1'), ('7','8'), ('8','1'), ('9','1'), ('10','1')]
    buttons.append([[
            InlineKeyboardButton(
                text=i[0],
                callback_data=i[1]),
            InlineKeyboardButton(
                text=i[0],
                callback_data=i[1])] for i in state_class])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


bot_functions_kb = InlineKeyboardMarkup(
    # меню сформированного фильтра
    inline_keyboard=[[
        InlineKeyboardButton(
            text="Назад",
            callback_data="start_menu_help_hide")]])


async def params_menu_kb(callback, db, help_flag=False):
    # меню списка фильтров
    help_callback = 'params_menu_help_show' if help_flag is True else 'params_menu_help_hide'
    help_text = "🔎 Помощь" if help_flag is True else "🔎 Скрыть помощь"
    user_id = callback.from_user.id
    search_params_cursor = await db.execute(f"SELECT udata.search_param, udata.is_active, udata.id FROM user "
                                            f"INNER JOIN udata on user.id = udata.user_id "
                                            f"WHERE user.tel_id = {user_id}")
    search_params = await search_params_cursor.fetchall()
    buttons = []
    if search_params == buttons:
        pass
    else:
        buttons = [[
            InlineKeyboardButton(
                text=decode_filter_short(i[0])[7:],
                callback_data=f'f_{i[2]}_show'),
            InlineKeyboardButton(
                text=str(i[1]).replace('1', 'Отключить').replace('0', 'Активировать'),
                callback_data=f'f_{i[2]}_{i[1]}'),
            InlineKeyboardButton(
                text='Удалить',
                callback_data=f'f_{i[2]}_del')] for i in search_params]
    buttons.append([
        InlineKeyboardButton(
            text='Назад',
            callback_data='start_menu_help_hide'),
        InlineKeyboardButton(
            text='Добавить фильтр',
            callback_data='create_search')])
    buttons.append([
        InlineKeyboardButton(
            text=help_text,
            callback_data=help_callback)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def filter_menu_kb(callback, cars_count):
    # меню опций фильтра, заказ отчета (callback = udata.id )
    filter_id = callback.data.split('_')[1]
    buttons = [[
        InlineKeyboardButton(
            text="🖼 Главное меню",
            callback_data="start_menu_help_hide")], [
        InlineKeyboardButton(
            text="Назад",
            callback_data="show_search")]]
    if cars_count > 0:
        buttons[0].insert(0, InlineKeyboardButton(
            text="📝 Создать отчет",
            callback_data=f'f_{filter_id}_rep'))
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def car_message_kb():
    buttons = [[
        InlineKeyboardButton(
            text="Отслеживать цену",
            callback_data="car_follow"),
        InlineKeyboardButton(
            text="Удалить",
            callback_data="message_delete")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def stalk_menu_kb(callback, db, help_flag=False):
    # меню списка слкжки
    help_callback = 'stalk_menu_help_show' if help_flag is True else 'stalk_menu_help_hide'
    help_text = "🔎 Помощь" if help_flag is True else "🔎 Скрыть помощь"
    user_id = callback.from_user.id
    search_params_cursor = await db.execute(f"SELECT ucars.url, ucars.id FROM user "
                                            f"INNER JOIN ucars on user.id = ucars.user_id "
                                            f"WHERE user.tel_id = {user_id}")
    search_params = await search_params_cursor.fetchall()
    buttons = []
    if search_params == buttons:
        pass
    else:
        buttons = [[
            InlineKeyboardButton(
                text=' '.join(i[0].split('/')[3:]),
                url=i[0],
                callback_data=f's_{i[1]}_show'),
            InlineKeyboardButton(
                text='Удалить',
                callback_data=f's_{i[1]}_del')]
            for i in search_params]
    buttons.append([
        InlineKeyboardButton(
            text='Назад',
            callback_data='start_menu_help_hide'),
        InlineKeyboardButton(
            text='Добавить ссылку',
            callback_data='add_stalk')])
    buttons.append([
        InlineKeyboardButton(
            text=help_text,
            callback_data=help_callback)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


add_stalk_kb = InlineKeyboardMarkup(
    # меню добавление слежки
    inline_keyboard=[[
        InlineKeyboardButton(
            text="Назад",
            callback_data="show_stalk")]])
