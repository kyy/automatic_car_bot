from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

from logic.codec_filter import decode_filter_short
from logic.constant import CF, PAGINATION
from logic.func import check_count_cars_active, check_count_filters_active
from logic.kb_fu import pagination
from logic.text import TXT


def single_row_kb(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def multi_row_kb(items: list[str], columns: int = 4, del_sb=False, **kwargs) -> ReplyKeyboardMarkup:
    kb = [KeyboardButton(text=i) for i in items]
    kb = [kb[i: i + columns] for i in range(0, len(kb), columns)]  # группируем на подсписки длинной columns
    kb_control = [[KeyboardButton(text=i) for i in (CF[:-1] if del_sb is True else CF)]]
    kb_control.extend(kb)
    return ReplyKeyboardMarkup(**kwargs, keyboard=kb_control, resize_keyboard=False)


def start_menu_kb(help_flag):
    # главное меню
    help_callback = f"start_menu_help_show" if help_flag is True else "start_menu_help_hide"
    help_text = TXT["btn_show_help"] if help_flag is True else TXT["btn_hide_help"]
    buttons = [
        [InlineKeyboardButton(text=TXT["btn_search"], callback_data="show_search")],
        [InlineKeyboardButton(text=TXT["btn_stalk"], callback_data="show_stalk")],
        [
            InlineKeyboardButton(text=TXT["btn_info"], callback_data="bot_functions"),
            InlineKeyboardButton(text=help_text, callback_data=help_callback),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_menu_kb(fsm):
    # меню сформированного фильтра
    f = (decode_filter_short(lists=fsm)).split(" | ")
    state_class = [
        ([f[0], "edit_search"], [f[1], "cb_model"]),
        ([f[2], "cb_motor"], [f[3], "cb_transmission"]),
        ([f[4], "cb_year_from"], [f[5], "cb_year_to"]),
        ([f[6], "cb_price_from"], [f[7], "cb_price_to"]),
        ([f[8], "cb_dimension_from"], [f[9], "cb_dimension_to"]),
    ]
    buttons = [
        [
            InlineKeyboardButton(text=i[0][0], callback_data=i[0][1]),
            InlineKeyboardButton(text=i[1][0], callback_data=i[1][1]),
        ]
        for i in state_class
    ]
    buttons.extend(
        [
            [InlineKeyboardButton(text=TXT["btn_save"], callback_data="save_search")],
            [InlineKeyboardButton(text=TXT["btn_cancel"], callback_data="start_menu_help_hide")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


bot_functions_kb = InlineKeyboardMarkup(
    # меню функций бота
    inline_keyboard=[[InlineKeyboardButton(text=TXT["btn_back"], callback_data="start_menu_help_hide")]]
)


async def params_menu_kb(callback, db, help_flag=False, cur_page=1):
    # меню списка фильтров
    tel_id = callback.from_user.id

    status_filters_active = await check_count_filters_active(tel_id)

    help_callback = f"params_menu_help_show_{cur_page}" if help_flag is True else f"params_menu_help_hide_{cur_page}"
    help_text = TXT["btn_show_help"] if help_flag is True else TXT["btn_hide_help"]

    search_params_cursor = await db.execute(
        f"SELECT udata.search_param, udata.is_active, udata.id FROM user "
        f"INNER JOIN udata on user.id = udata.user_id "
        f"WHERE user.tel_id = {tel_id}"
    )
    search_params = await search_params_cursor.fetchall()
    buttons = []
    if search_params == buttons:
        pass
    else:
        search_params, pagination_buttons, del_pages = pagination(
            data=search_params, name="params", ikb=InlineKeyboardButton, per_page=PAGINATION, cur_page=cur_page
        )
        buttons = [
            [
                InlineKeyboardButton(text=decode_filter_short(i[0][7:]), callback_data=f"f_{i[2]}_show"),
                InlineKeyboardButton(
                    text=str(i[1]).replace("1", TXT["btn_off"]).replace("0", TXT["btn_on"]),
                    callback_data=f"f_{i[2]}_{cur_page}_{status_filters_active}_{i[1]}",
                ),
                InlineKeyboardButton(text=TXT["btn_delete"], callback_data=f"f_{i[2]}_{del_pages}_del"),
            ]
            for i in search_params
        ]
        buttons.append(pagination_buttons)
    buttons.append([InlineKeyboardButton(text=TXT["btn_add_filter"], callback_data="create_search")])
    buttons.append(
        [
            InlineKeyboardButton(text=TXT["btn_back"], callback_data="start_menu_help_hide"),
            InlineKeyboardButton(text=help_text, callback_data=help_callback),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def filter_menu_kb(callback, cars_count):
    # меню опций фильтра, заказ отчета (callback = udata.id )
    filter_id = callback.data.split("_")[1]
    buttons = [
        [
            InlineKeyboardButton(text=TXT["btn_back"], callback_data="show_search"),
            InlineKeyboardButton(text=TXT["btn_start_menu"], callback_data="start_menu_help_hide"),
        ]
    ]
    if cars_count > 0:
        buttons.insert(0, [InlineKeyboardButton(text=TXT["btn_rep_filter"], callback_data=f"f_{filter_id}_rep")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def car_message_kb(url):
    # меню отследить или удалить сообщение
    """
    :param url: полная ссылка на объявление
    :return:
    """
    url = url.split('/')
    car_id = url[-1]
    domen = url[2]

    buttons = [
        [
            InlineKeyboardButton(text=TXT["btn_stalk_price"], callback_data="car_follow"),
            InlineKeyboardButton(text=TXT["btn_car_details"], callback_data=f"{domen}_{car_id}_research"),
            InlineKeyboardButton(text=TXT["btn_delete"], callback_data="message_delete"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def car_message_details_kb():
    # меню отследить или удалить сообщение
    """
    :param url: полная ссылка на объявление
    :return:
    """

    buttons = [
        [
            InlineKeyboardButton(text=TXT["btn_stalk_price"], callback_data="car_follow"),
            InlineKeyboardButton(text=TXT["btn_delete"], callback_data="message_delete"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def car_price_message_kb(url):
    # меню удалить сообщение
    url = url.split('/')
    car_id = url[-1]
    domen = url[2]
    buttons = [
        [
            InlineKeyboardButton(text=TXT["btn_car_details"], callback_data=f"{domen}_{car_id}_price_research"),
            InlineKeyboardButton(text=TXT["btn_delete"], callback_data="message_delete"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def delete_message_kb():
    # меню удалить сообщение
    buttons = [
        [
            InlineKeyboardButton(text=TXT["btn_delete"], callback_data="message_delete"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def stalk_menu_kb(callback, db, help_flag=False, cur_page=1):
    # меню списка слежки
    tel_id = callback.from_user.id

    status_cars_active = await check_count_cars_active(tel_id)

    help_callback = f"stalk_menu_help_show_{cur_page}" if help_flag is True else f"stalk_menu_help_hide_{cur_page}"
    help_text = TXT["btn_show_help"] if help_flag is True else TXT["btn_hide_help"]

    search_params_cursor = await db.execute(
        f"SELECT ucars.url, ucars.is_active, ucars.id FROM user "
        f"INNER JOIN ucars on user.id = ucars.user_id "
        f"WHERE user.tel_id = {tel_id}"
    )
    search_params = await search_params_cursor.fetchall()
    buttons = []
    if search_params == buttons:
        pass
    else:
        search_params, pagination_buttons, del_page = pagination(
            data=search_params, name="stalk", ikb=InlineKeyboardButton, per_page=PAGINATION, cur_page=cur_page
        )

        buttons = [
            [
                InlineKeyboardButton(text=" ".join(i[0].split("/")[3:]), url=i[0], callback_data=f"s_{i[2]}_show"),

                InlineKeyboardButton(text=str(i[1]).replace("1", TXT["btn_off"]).replace("0", TXT["btn_on"]),
                                     callback_data=f"s_{i[2]}_{cur_page}_{status_cars_active}_{i[1]}"),

                InlineKeyboardButton(text=TXT["btn_delete"], callback_data=f"s_{i[2]}_{del_page}_del")
            ]
            for i in search_params
        ]
        buttons.append(pagination_buttons)

    buttons.append([InlineKeyboardButton(text=TXT["btn_add_stalk_url"], callback_data="add_stalk")])

    buttons.append(
        [
            InlineKeyboardButton(text=TXT["btn_back"], callback_data="start_menu_help_hide"),
            InlineKeyboardButton(text=help_text, callback_data=help_callback),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


add_stalk_kb = InlineKeyboardMarkup(
    # меню добавление слежки
    inline_keyboard=[[InlineKeyboardButton(text=TXT["btn_back"], callback_data="show_stalk")]]
)


def donate_kb():
    # меню доната
    buttons = [
        [
            InlineKeyboardButton(
                text="сделать перевод",
                web_app=WebAppInfo(url="https://yoomoney.ru/to/4100118330778097"),
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def asky_kb(tel_id):
    # меню поделится ботом
    buttons = [
        [
            InlineKeyboardButton(
                text="Поделится в Telegram",
                url=f"https://t.me/share/url?url=https://t.me/Automaticcarbot?start={tel_id}")
        ],
        [
            InlineKeyboardButton(
                text="Поделится в Vkontakte",
                url=f"https://vk.com/share.php?url=https://t.me/Automaticcarbot?start={tel_id}")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
