from logic.constant import ROOT_URL, BOT

TXT = dict(
    info_start_menu_help='<b>Несколько команд для начала:</b>\n'
                         '<i>Команды также работают без слеша "/"</i>\n'
                         '- <b>/start</b>  или  <b>/s</b> - открыть главное меню.\n'
                         '- <b>/filter</b>  или  <b>/f</b> - создать поиск.\n'
                         '- <b>/help</b>  или  <b>/h</b> - покажет все команды.\n',

    info_filter_menu_help='- Нажав на фильтр можно увидеть сколько машин удовлетворяет вашему поиску.\n '
                          '- Также можно создать сравнительный отчет текущих объявлений.\n'
                          '- Отчет представляет собой интерактивный PDF-файл с ссылками на объявления.\n',

    info_stalk_menu_help='Если заинтересовала какая-нибудь машина, ссылку на нее можно отправить мне,'
                         ' я уведомлю если продавец изменит цену.',

    info_save_search='Все текущие объявления можно сформировать как отчет в управлении фильтрами.\n',

    info_bot='<b>Основные функции:</b>\n'
             '- Автоматическая рассылка свежих объявлений.\n'
             '- Отслеживание изменения цен.\n'
             '- Формирование отчета с текущими объявлениями.\n'
             '\n'
             '<b>Cобираю информацию с сайтов:</b>\n'
             + "- " + str("- ".join([i + " \n" for i in ROOT_URL.values()])) +
             '\n'
             '<a href="{telegram}"><i>{telegram_name}</i></a>  💬\n'
             '<i>{email}</i>  ✉\n'
             '<i>{site}</i>  🌐\n',

    info_filter="📌 {decode_filter_short}\n"
                "\n"
                "📊 Доступные объявления:\n"
                "\n"
                "<a href='{av_l}'>av.by</a> - {all_av}.\n"
                "<a href='{abw_l}'>abw.by</a> - {all_abw}.\n"
                "<a href='{onliner_l}'>onliner.by</a> - {all_onliner}.\n"
                "<a href='{kufar_l}'>kufar.by</a> - {all_kufar}.\n"
                "\n"
                " Сформируйте, как можно уже поисковый фильтр.\n",

    info_start_menu='Главное меню\n',

    info_filter_menu='- Здесь я храню фильтры поиска.\n'
                     '- Как только появится подходящая машина - я дам знать',

    info_stalk_menu='Я внимательно слежу за ценами объявлений в этом списке',
    info_add_stalk_menu='Отправьте сюда ссылку. Можно отправить несколько разделив пробелом.',
    info_donate='<b>Хотите отблагодарить монетой?</b>\n'
                '\n'
                '<i>Сумма пожертвований указана в ₽</i>',
    info_asky='<b>Расскажи своим друзьями обо мне.</b>\n'
              '\n'
              '<i>Приглашенных людей: <b>{ref}</b></i>\n'
              '\n'
              f'<code>{BOT["url"]}' + '?start={tel_id}</code>',

    btn_search='🔎 Автопоиск',
    btn_stalk='📉 Отследить цену',
    btn_info='🦾 Мои возможности',
    btn_show_help='🆘 Помощь',
    btn_hide_help='☝ Скрыть Помощь',
    btn_cancel='❌ Отмена',
    btn_save='✅ Сохранить',
    btn_back='« Назад',
    btn_delete='🗑 Убрать',
    btn_add_filter='+ Добавить фильтр',
    btn_off='⏹ Стоп',
    btn_on='▶ Пуск',
    btn_start_menu='« Главное меню',
    btn_rep_filter='📝 Создать отчет',
    btn_stalk_price='📉 Отслеживать',
    btn_add_stalk_url='+ Добавить машину',
    btn_page_left='<',
    btn_page_right='>',
    btn_car_details='🔎 Подробности',
    btn_admin='👑 admin',

    msg_error='⚠ Произошла ошибка',
    msg_collect_data='⏳ Собираем данные',
    msg_cooking_rep='⌛ Готовим отчет',
    msg_empty_filter='⚠ Фильтр пуст. Воспользуйтесь командой /filter или /start',
    msg_finish_filter='Проверьте параметры, если необходимо отредактируйте перед сохранением.'
                      ' Постарайтесь сузить поиск.',
    msg_added_url='{url}\n⚡ ссылка добавлена',
    msg_stalking_url='{url}\n⚠ ссылка уже отслеживается',

    msg_error_url='⚠ Неверная ссылка.\n'
                  f'На данный момент слежу за: {" | ".join([i for i in ROOT_URL.values()])}.',
    msg_last_filter='📌 Последний фильтр:\n {decode_filter_short}',

    msg_error_filter_input='⚠ Пожалуйста, выберите одно из значений из предложенного списка.',
    msg_unknown_command='⚠ Команда не найдена\n'
                        '\n'
                        'Доступные команды:\n'
                        '{all_commands}',

    msg_com='Доступные команды:\n'
            '{all_commands}\n',

    msg_wrong_filter='⚠ Проверьте не противоречат ли параметры друг другу.',
    msg_dublicate_filter='⚠ Такой фильтр уже добавлен.',
    msg_limit='⚠ Вы превысили лимит.',
    msg_limit_Subs='⚠ Вы превысили лимит.',

    f_brand='📌 бренд автомобиля',
    f_model='📌 модель',
    f_motor='📌 тип топлива',
    f_transmission='📌 тип трансмиссии',
    f_year_from='📌 с какого года',
    f_year_to='📌 по какой год',
    f_price_from='📌 минимальная цена',
    f_price_to='📌 максимальная цена',
    f_dimension_from='📌 минимальный объем двигателя',
    f_dimension_to='📌 максимальный объем двигателя',

    fi_brand='имя бренда',
    fi_model='имя модели',
    fi_motor='тип топлива',
    fi_transmission='тип трансмиссии',
    fi_year_from='год от',
    fi_year_to='год по',
    fi_price_from='стоимость от',
    fi_price_to='стоимость до',
    fi_dimension_from='объем двигателя от',
    fi_dimension_to='объем двигателя до',
)

TEXT_DETAILS = (
    "{url}\n"
    "<i>${price}</i>\n"
    "<b>{brand} {model} {generation} {year}</b>\n"
    "\n"
    "<i>{motor} {dimension}л\n"
    "{km} км\n"
    "{transmission} {drive} привод\n"
    "{color} {typec}</i>\n"
    "\n"
    "Статус: <i>{status}</i>\n"
    "Дней в продаже: <i>{days}</i>\n"
    "VIN: <code>{vin}</code>\n"
    "VIN проверен: <i>{vin_check}</i>\n"
    "Город: <i>{city}</i>\n"
    "\n"
    "<i>{descr} ...</i>\n"
    "\n"
)
