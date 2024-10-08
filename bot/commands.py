from aiogram.types import BotCommand

commands = [
    BotCommand(
        command="/start",
        description="📋  Меню",
        full_description=" Отобразит главное меню в любой необходимый момент."
                         " Также сбрасывает выбранные параметры текущего фильтра",
    ),
    BotCommand(
        command="/filter",
        description="⚙  Создать поиск ",
        full_description=" Пошаговый помощник, поможет вам сгенерировать фильтр для получения свежих объявлений.",
    ),
    BotCommand(
        command="/build",
        description="🚗  Сохранить поиск",
        full_description=" Отобразит сформированный фильтр."
                         " Можно применить при формировании фильтра, позволит пропустить шаги помощника."
                         " Отобразит клавиатуру позволяющую изменить параметры, сохранить/отменить фильтр.",
    ),
    BotCommand(
        command="/donate",
        description="💸  Сказать спасибо",
        full_description=" Поддержать проект"
    ),
    BotCommand(
        command="/tell",
        description="📢  Рассказать друзьям",
        full_description=" Поделись ссылкой на меня со совими друзьями, кому я могу быть полезен."
    ),
    BotCommand(
        command="/help",
        description="⁉  Помощь",
        full_description=" Все команды с подробным описанием."
    ),
]
