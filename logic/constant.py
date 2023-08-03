
WORK_PARSE_DELTA = 2   # частота проверки новых обявллений в часах
REPORT_PARSE_LIMIT_PAGES = 5  # лимит страниц парсиинга для отчета


SS = '+'    # split symbol in filter
SB = '[выбрать все]'    # skip button on keyboards
FSB = '?'    # skip-liter in filter
EB = '[закончить]'
CF = [EB, SB]    # 1st row of keyboard in creating filters

# constants of columns:keyboards: max = 8, default = 4
COL_MOTOR = 3
COL_YEARS = 5
COL_COST = 5
COL_DIMENSION = 8

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
