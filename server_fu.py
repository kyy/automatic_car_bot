from datetime import datetime

from logic.constant import (
    CARS_ADD_LIMIT_ACTIVE, FILTER_ADD_LIMIT_ACTIVE, BOT
)

FAQ = [
    (
        'Сколько стоят мои услуги? ',
        'Бесплано предоставляется создание поисковых фильтров и отслеживание цен конкретных объявлений, '
        'но есть ограничениене по одновременной работе: '
        f'не более {FILTER_ADD_LIMIT_ACTIVE} фильтров и '
        f'не более {CARS_ADD_LIMIT_ACTIVE} отслеживаний. '
        'Для расширения лимитов планируется введение платной подписки. '
    ),
    (
        'Возможно ли добавить индивидульный функционал боту? ',
        'Я открыт для для любого взаимодействия, рассмотрю любые предложения касающиеся моему развитию. '
        'С удовольствием учту пожелание пользвателей. '
    ),
    (
        'Кому я буду полезен? ',
        'Человеку, который уенит сове время.'
    ),
]

BOT.update(
    {
        'year': datetime.now().year,
    }
)
