from datetime import datetime

LOGO = 'logic/static/logo.png'
FOLDER_PARSE = 'logic/database/parse/'

LEN_DESCRIPTION = 700

MM = dict(
    MIN_YEAR=2000,
    MAX_YEAR=datetime.now().year,
    MIN_DIM=1,
    MAX_DIM=9,
    STEP_DIM=0.1,
    MIN_COST=500,
    MAX_COST=100000,
    STEP_COST=2500,
)

WORK_PARSE_CARS_DELTA = 1  # частота проверки новых объявллений в часах
WORK_PARSE_PRICE_DELTA = 3  # частота проверки цен в часах

AV_WORK_PARSE_PRICE_DELTA_CORRECTION = 0  # поправка на часовой пояс в минутах
KUFAR_WORK_PARSE_PRICE_DELTA_CORRECTION = 0
ONLINER_WORK_PARSE_PRICE_DELTA_CORRECTION = 0

REPORT_PARSE_LIMIT_PAGES = 2  # лимит страниц парсиинга для отчета PDF (1стр = 25 машин)
PARSE_LIMIT_PAGES = 4  # лимит страниц парсиинга (1стр = 20 или 25 машин)

CARS_ADD_LIMIT = 10
FILTER_ADD_LIMIT = 10

FILTER_ADD_LIMIT_ACTIVE = 5
CARS_ADD_LIMIT_ACTIVE = 5

SUBS_CARS_ADD_LIMIT = 50
SUBS_FILTER_ADD_LIMIT = 50

SUBS_FILTER_ADD_LIMIT_ACTIVE = 15
SUBS_CARS_ADD_LIMIT_ACTIVE = 15

SS = "+"  # split symbol in filter
SB = "✅ выбрать все"  # skip button on keyboards
FSB = "?"  # skip-liter in filter
EB = "❎ завершить"
CF = [EB, SB]  # 1st row of keyboard in creating filters

COL = dict(MOTOR=3, YEARS=5, COST=5, DIMENSION=8)  # constants of columns:keyboards: max = 8, default = 4

PAGINATION = 5

ROOT_URL = dict(
    AV="https://cars.av.by/",
    ONLINER="https://ab.onliner.by/",
    KUFAR="https://auto.kufar.by/",
)

API_DOMEN = dict(
    AV="api.av.by",
    ONLINER="ab.onliner.by",
    KUFAR="api.kufar.by",
)

DOMEN = dict(
    AV="av.by",
    ONLINER="onliner.by",
    KUFAR="kufar.by",
)

MOTOR_DICT = {
    "бензин": "b",
    "бензин (пропан-бутан)": "bpb",
    "бензин (метан)": "bm",
    "бензин (гибрид)": "bg",
    "дизель": "d",
    "дизель (гибрид)": "dg",
    "электро": "e",
}

MOTOR = ["бензин", "дизель", "электро", "дизель (гибрид)", "бензин (метан)", "бензин (гибрид)", "бензин (пропан-бутан)"]

TRANSMISSION = ["автомат", "механика"]

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/109.0.0.0 Safari/537.36",
    "accept": "*/*",
}

HEADERS_JSON = HEADERS.update({"content-type": "application/json"})

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
    chosen_dimension_max=SB,
)
