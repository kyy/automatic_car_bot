from aiogram.types import BotCommand


commands = [
        BotCommand(
            command='/start',
            description="📋  Меню",
            full_description=' Отобразит главное меню в любой необходимый момент.'
        ),

        BotCommand(
            command='/filter',
            description="⚙  Поиск ",
            full_description=' Пошаговый помощник, поможет вам сгенерировать фильтр для получения свежих объявлений.'
        ),
        BotCommand(
            command='/build',
            description='🚗  Фильтр',
            full_description=' Отобразит сформированный фильтр.'
                             ' Можно применить при формировании фильтра, позволит пропустить шаги помощника.'
                             ' Отобразит клавиатуру позволяющую изменить параметры, сохранить/отменить фильтр.'
        ),

        BotCommand(
            command='/reset',
            description='👎  Прервать',
            full_description=' Отменит текущее действие.'
                             ' Скроет клавиатуру и очистит параметры текущего фильтра.'
        ),
        BotCommand(
            command='/help',
            description='⁉  Помощь',
            full_description=' Все команды с подробным описанием.'
        )
]

