from datetime import datetime

from logic.constant import FSB, MOTOR_DICT, SS
from logic.kb_fu import get_cost, get_years, get_dimension


# encode from strings = 'Citroen|C4|b|a|-|-|-|-|-|-' or list to full description
def decode_filter_short(string: str = None, lists: list = None, sep: str = SS):
    motor_dict_reverse = dict(zip(MOTOR_DICT.values(), MOTOR_DICT.keys()))
    if lists is None:
        c = (string.split(sep=sep))
        if c[2] in motor_dict_reverse:
            c[2] = motor_dict_reverse[c[2]]
        if c[8] != FSB:
            c[8] = str(int(c[8]) / 1000)
        if c[9] != FSB:
            c[9] = str(int(c[9]) / 1000)
        if c[3] != FSB:
            c[3] = 'автомат' if c[3] == 'a' else 'механика'
    else:
        c = lists
    text = f"{c[0].replace(FSB, 'все бренды')} | {c[1].replace(FSB, 'все модели')} | " \
           f"{c[2].replace(FSB, 'все двигатели')} | {c[3].replace(FSB, 'все трансмиссии')} | " \
           f"{c[4].replace(FSB, get_years()[0])}г | {c[5].replace(FSB, str(datetime.now().year))}г | " \
           f"{c[6].replace(FSB, get_cost()[0])}$ | {c[7].replace(FSB, str(get_cost()[-1]))}$ | " \
           f"{c[8].replace(FSB, get_dimension()[0])}л | {c[9].replace(FSB, str(get_dimension()[-1]))}л"
    return text if lists else text.replace('\n', ' | ')


# decode from lists of discription to 'filter=Citroen|C4|b|a|-|-|-|-|-|-'
def code_filter_short(cc: list = None):
    if cc[3] != FSB:
        cc[3] = 'a' if cc[3] == 'автомат' else 'm'
    if cc[2] in MOTOR_DICT:
        cc[2] = MOTOR_DICT[cc[2]]
    if cc[8] != FSB:
        cc[8] = str(int(cc[8].replace('.', '')) * 100)
    if cc[9] != FSB:
        cc[9] = str(int(cc[9].replace('.', '')) * 100)
    return 'filter=' + SS.join(cc)
