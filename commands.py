from aiogram.types import BotCommand


commands = [
        BotCommand(
            command='/start',
            description="Главное меню",
            full_description=' Отобразит главное меню в любой необъодимый момент.'
        ),

        BotCommand(
            command='/filter',
            description="Создать фильтр",
            full_description=' Пошаговый помощник, поможет вам сгенерировать фильтр для получения свежих объявлений.'
        ),
        BotCommand(
            command='/build',
            description='Показать текущий фильтр',
            full_description=' Отобразит сформированный фильтр.'
                             ' Можно применить при формировании фильтра, позволит пропустить шаги помощника.'
                             ' Отобразит клавиатуру позволяющую изменить параметры, сохранить/отменить фильтр.'
        ),

        BotCommand(
            command='/reset',
            description='Прервать действие',
            full_description=' Отменит текущее действие.'
                             ' Скроет клавиатуру'
        ),
        BotCommand(
            command='/com',
            description="Показать команды",
            full_description=' Отобразит все команды.'
        ),
        BotCommand(
            command='/help',
            description='Помощь',
            full_description=' Все команды с подробным описанием.'
        )
]

