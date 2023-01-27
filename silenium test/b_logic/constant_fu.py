import numpy as np
import datetime
import time

s_s = '+'    # split symbol in filter
s_b = '?'    # skip button on keyboards

# constants of columns:keyboards: max = 8, default = 4
columns_motor = 3
columns_years = 5
columns_cost = 5
columns_dimension = 8

# source of data for buttons
# make '' for delete button

motor_dict = {'бензин': 'b', 'бензин (пропан-бутан)': 'bpb', 'бензин (метан)': 'bm', 'бензин (гибрид)': 'bg',
              'дизель': 'd', 'дизель (гибрид)': 'dg', 'электро': 'e'}

motor = [s_b] + \
        ['бензин', 'дизель', 'электро', 'дизель (гибрид)', 'бензин (метан)', 'бензин (гибрид)', 'бензин (пропан-бутан)']

transmission = [s_b] + ['автомат', 'механика']


def get_brands() -> list[str]:
    return sorted(np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item())


def get_models(brand: str) -> list[str]:
    return [s_b] + sorted(np.load(f'base_data_av_by/models_part_url/{brand}.npy', allow_pickle=True).item())


def get_years(from_year: int = 1990, to_year=datetime.datetime.now().year) -> list[str]:
    return [s_b] + [str(i) for i in range(from_year, to_year + 1)]


def get_dimension(from_dim: float = 1, to_dim: float = 9, step: float = 0.1) -> list[str]:
    return [s_b] + [str(round(i, 1)) for i in np.arange(from_dim, to_dim + step, step)]


def get_cost(from_cost: int = 500, to_cost: int = 100000, step: int = 2500) -> list[str]:
    return [s_b] + [str(i) for i in range(from_cost, to_cost - step, step)]


# encode from strings = 'Citroen|C4|b|a|-|-|-|-|-|-' or list to full description
def decode_filter_short(string: str = None, lists: list = None, sep: str = s_s):
    motor_dict_reverse = dict(zip(motor_dict.values(), motor_dict.keys()))
    if lists is None:
        c = (string.split(sep=sep))
        if c[2] in motor_dict_reverse:
            c[2] = motor_dict_reverse[c[2]]
        if c[8] != s_b:
            c[8] = str(int(c[8]) / 1000)
        if c[9] != s_b:
            c[9] = str(int(c[9]) / 1000)
        if c[3] != s_b:
            c[3] = 'автомат' if c[3] == 'a' else 'механика'
    else:
        c = lists
    text = f"{c[0].replace(s_b, '<все бренды>')} {c[1].replace(s_b, '<все модели>')}\n" \
           f"{c[2].replace(s_b, '<все типы двигателей>')} {c[3].replace(s_b, '<все типы трансмиссий>')}\n" \
           f"с {c[4].replace(s_b, get_years()[1])}  по {c[5].replace(s_b, str(datetime.datetime.now().year))} г\n" \
           f"от {c[6].replace(s_b, get_cost()[1])}  до {c[7].replace(s_b, str(get_cost()[-1]))} $\n" \
           f"от {c[8].replace(s_b, get_dimension()[1])}  до {c[9].replace(s_b, str(get_dimension()[-1]))} л"
    return text if lists else text.replace('\n', ' | ')


# decode from lists of discription to 'filter=Citroen|C4|b|a|-|-|-|-|-|-'
def code_filter_short(cc: list = None):
    if cc[3] != s_b:
        cc[3] = 'a' if cc[3] == 'автомат' else 'm'
    if cc[2] in motor_dict:
        cc[2] = motor_dict[cc[2]]
    if cc[8] != s_b:
        cc[8] = str(int(cc[8].replace('.', '')) * 100)
    if cc[9] != s_b:
        cc[9] = str(int(cc[9].replace('.', '')) * 100)
    return 'filter=' + s_s.join(cc)


def time_data(number):
    n = 3+(number/5) if number <= 25 else (number/25) * 17
    return time.strftime("%M мин %S с", time.gmtime(n))
