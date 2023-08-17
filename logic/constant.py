WORK_PARSE_CARS_DELTA = 2   # частота проверки новых объявллений в часах
WORK_PARSE_PRICE_DELTA = 3  # частота проверки цен в часах
REPORT_PARSE_LIMIT_PAGES = 4  # лимит страниц парсиинга для отчета PDF (1стр = 25 машин)
PARSE_LIMIT_PAGES = 4   # лимит страниц парсиинга (1стр = 25 машин)

SS = '+'    # split symbol in filter
SB = '✅ выбрать все'    # skip button on keyboards
FSB = '?'    # skip-liter in filter
EB = '❎ завершить'
CF = [EB, SB]    # 1st row of keyboard in creating filters

COL = dict(MOTOR=3, YEARS=5, COST=5, DIMENSION=8)  # constants of columns:keyboards: max = 8, default = 4

PAGINATION = 5
COST_STEP = 2500   # param:step in func.get_cost

AV_ROOT = 'https://cars.av.by/'
ABW_ROOT = 'https://abw.by/'
ONLINER_ROOT = 'https://ab.onliner.by/'

AV_API = 'api.av.by'
ABW_API = 'b.abw.by'
ONLINER_API = 'ab.onliner.by'

MOTOR_DICT = {
    'бензин': 'b',
    'бензин (пропан-бутан)': 'bpb',
    'бензин (метан)': 'bm',
    'бензин (гибрид)': 'bg',
    'дизель': 'd',
    'дизель (гибрид)': 'dg',
    'электро': 'e'}

MOTOR = ['бензин', 'дизель', 'электро', 'дизель (гибрид)', 'бензин (метан)', 'бензин (гибрид)', 'бензин (пропан-бутан)']

TRANSMISSION = ['автомат', 'механика']

HEADERS = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*'}

HEADERS_JSON = HEADERS.update({'content-type': 'application/json'})

DEFAULT = dict(
    chosen_brand=SB,
    chosen_model=SB,
    chosen_motor=SB,
    chosen_transmission=SB,
    chosen_year_from=SB,
    chosen_year_to=SB,
    chosen_cost_min=SB,
    chosen_cost_max=SB,
    chosen_dimension_min=SB,
    chosen_dimension_max=SB
)


'https://habr.com/ru/companies/vk/articles/528490/'
