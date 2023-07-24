from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardBuilder
from aiocache import cached
from logic.func import decode_filter_short


def single_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def multi_row_keyboard(items: list[str], columns: int = 4, **kwargs) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(*[KeyboardButton(text=item) for item in items]).adjust(columns)
    return builder.as_markup(**kwargs)


def start_menu(help_flag):
    # главное меню
    help_callback = 'start_menu_help_show' if help_flag is True else 'start_menu_help_hide'
    help_text = "🔎 Помощь" if help_flag is True else "🔎 Скрыть помощь"
    buttons = [[
        InlineKeyboardButton(
            text="🖼 Мои фильтры",
            callback_data="show_search")], [
        InlineKeyboardButton(
            text=help_text,
            callback_data=help_callback)]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


result_menu = InlineKeyboardMarkup(
    # меню сформированного фильтра
    inline_keyboard=[[
        InlineKeyboardButton(
            text="📝 Сохранить фильтр",
            callback_data="save_search"),
        InlineKeyboardButton(
            text="🖼 Отмена",
            callback_data="start_menu_help_hide")], [
        InlineKeyboardButton(
            text="🔎 Помощь",
            callback_data="start_menu_help_show")]])


async def params_menu(callback, db, help_flag=False):
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
                callback_data=f'f_{user_id}_{i[2]}_{i[1]}'),
            InlineKeyboardButton(
                text='Удалить',
                callback_data=f'f_{user_id}_{i[2]}_del')]
            for i in search_params]
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


def filter_menu(callback, cars_count):
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
