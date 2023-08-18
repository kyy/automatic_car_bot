from logic.constant import AV_ROOT, KUFAR_ROOT, ABW_ROOT, ONLINER_ROOT

TXT = dict(
    info_start_menu_help='ℹ <b>Вот несколько команд для начала:</b>\n'
                         '\n'
                         '⚡ <b>/start</b>  или  <b>/s</b> - открыть главное меню.\n'
                         '\n'
                         '⚡ <b>/filter</b>  или  <b>/f</b> - создать поиск.\n'
                         '\n'
                         '⚡ <b>/help</b>  или  <b>/h</b> - покажет все команды.',

    info_filter_menu_help='ℹ Нажав на фильтр можно заказать сравнительный отчет о всех активных объявлениях.\n'
                          '\n'
                          'ℹ Отчет представляет собой PDF-файл, первая колонка в таблице - ссылки на объявления.\n',

    info_stalk_menu_help='ℹ Тут все просто, запускаешь, останавливаешь или удаляешь ссылки.',

    info_save_search='ℹ Все текущие объявления можно сформировть как отчет в управлении фильтрами.\n',

    info_bot='ℹ <b>Основные функции:</b>\n'
             '\n'
             '🔸 Автоматическая рассылка свежих обявлений.\n'
             '🔸 Отслеживание изменения цен.\n'
             '🔸 Формирование отчета с текущими обявлениями.\n'
             '\n'
             'ℹ Cобираю информацию с таких сайтов как:\n'
             '\n'
             f'🔸{AV_ROOT}\n'
             f'🔸{KUFAR_ROOT}\n'
             f'🔸{ABW_ROOT}\n'
             f'🔸{ONLINER_ROOT}\n'
             + 87 * ' ' +
             '<a href="https://t.me/Xibolba">@Xibolba</a>  💬\n'
             + 65 * ' ' +
             'insider_2012@mail.ru  ✉\n',

    info_filter="📌 {decode_filter_short}\n"
                "\n"
                "📊 Доступные объявления:\n"
                "\n"
                "<a href='{av_l}'>av.by</a> - {all_av}.\n"
                "<a href='{abw_l}'>abw.by</a> - {all_abw}.\n"
                "<a href='{onliner_l}'>onliner.by</a> - {all_onliner}.\n"
                "<a href='{kufar_l}'>kufar.by</a> - {all_kufar}.\n"
                "\n"
                "⚠ Действует ограничение до {size} объявлений с 1 ресурса.\n",

    info_start_menu='ℹ Я помогу найти подходящий автомобиль.\n'
                    '\n'
                    'ℹ Просто создайте и сохраните необходимый поиск-фильтр, и занимайтесь привычными делами 🍿\n',

    info_filter_menu='ℹ Здесь я храню фильтры поиска.\n'
                    '\n'
                    'ℹ Как только появится подходящая машина - я дам знать',

    info_stalk_menu='ℹ Я внимательно слежу за ценами объявлений в этом списке',
    info_add_stalk_menu='ℹ Отправьте сюда ссылку. Можно отправить несколько разделив пробелом.',

    btn_search='🔎 Автопоиск',
    btn_stalk='📉 Оследить цену',
    btn_info='💪 Мои возможности',
    btn_show_help='❓ Помощь',
    btn_hide_help='❗ Скрыть Помощь',
    btn_cancel='❌ Отмена',
    btn_save='✅ Сохранить',
    btn_back='« Назад',
    btn_delete='🗑 Убрать',
    btn_add_filter='+ Добавить фильтр',
    btn_off='⏹ Стоп',
    btn_on='▶ Пуск',
    btn_start_menu='« Главное меню',
    btn_rep_filter='📝 Создать отчет',
    btn_stalk_price='📉 Отслеживать цену',
    btn_add_stalk_url='+ Добавить машину',
    btn_page_left='<',
    btn_page_right='>',

    msg_error='⚠ Произошла ошибка',
    msg_collect_data='⏳ Собираем данные',
    msg_cooking_rep='⌛ Готовим отчет',
    msg_empty_filter='⚠ Фильтр пуст. Воспользуйтесь командой /filter или /start',
    msg_finish_filter='ℹ Проверьте параметры, если необходимо отредактируйте перед сохранением. Постарайтесь сузить поиск.',
    msg_added_url='{url}\n⚡ ссылка добавлена',
    msg_stalking_url='{url}\n⚠ ссылка уже отслеживается',

    msg_error_url='⚠ Неверная ссылка.\n'
                  'На данный момент отслеживаю цены с cars.av.by и ab.onliner.by',
    msg_last_filter='📌 Последний фильтр:\n {decode_filter_short}',

    msg_error_filter_input='⚠ Пожалуйста, выберите одно из значений из предложенного списка.',
    msg_unknown_command='⚠ Команда не найдена\n'
                        '\n'
                        'Доступные команды:\n'
                        '{all_commands}',

    msg_com='ℹ Доступные команды:\n'
            '{all_commands}\n',

    msg_wrong_filter='⚠ Проверьте не противоречат ли параметры друг другу.',
    msg_dublicate_filter='⚠ Такой фильтр уже добавлен.',
    msg_reset_error='⚠ Мне кажется не стоит этого делать сейчас ☝',

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
