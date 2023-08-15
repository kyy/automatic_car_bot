
WORK_PARSE_CARS_DELTA = 2   # частота проверки новых объявллений в часах
WORK_PARSE_PRICE_DELTA = 3  # частота проверки цен в часах

REPORT_PARSE_LIMIT_PAGES = 5  # лимит страниц парсиинга для отчета PDF (1стр = 25 машин)


SS = '+'    # split symbol in filter
SB = '✅ выбрать все'    # skip button on keyboards
FSB = '?'    # skip-liter in filter
EB = '❎ завершить'
CF = [EB, SB]    # 1st row of keyboard in creating filters

# constants of columns:keyboards: max = 8, default = 4
COL_MOTOR = 3
COL_YEARS = 5
COL_COST = 5
COL_DIMENSION = 8

PAGINATION = 5

COST_STEP = 2500   # param:step in func.get_cost

# root links
AV_ROOT = 'https://cars.av.by/'
ABW_ROOT = 'https://abw.by/'
ONLINER_ROOT = 'https://ab.onliner.by/'

# api links
AV_API = 'api.av.by'
ABW_API = 'b.abw.by'
ONLINER_API = 'ab.onliner.by'


# parse of data for buttons
# make '' for delete button

MOTOR_DICT = {'бензин': 'b', 'бензин (пропан-бутан)': 'bpb', 'бензин (метан)': 'bm', 'бензин (гибрид)': 'bg',
              'дизель': 'd', 'дизель (гибрид)': 'dg', 'электро': 'e'}

MOTOR = ['бензин', 'дизель', 'электро', 'дизель (гибрид)', 'бензин (метан)', 'бензин (гибрид)', 'бензин (пропан-бутан)']

TRANSMISSION = ['автомат', 'механика']

HEADERS = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*'}

HEADERS_JSON = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}

DEFAULT = {'chosen_brand': SB,
           'chosen_model': SB,
           'chosen_motor': SB,
           'chosen_transmission': SB,
           'chosen_year_from': SB,
           'chosen_year_to': SB,
           'chosen_cost_min': SB,
           'chosen_cost_max': SB,
           'chosen_dimension_min': SB,
           'chosen_dimension_max': SB}

SUBSCRIPTION = {
    'max_filters': 2,
    'max_stulk': 2,
    'max_pdf': 2,
}


'https://habr.com/ru/companies/vk/articles/528490/'
