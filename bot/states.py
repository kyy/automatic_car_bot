from aiogram.fsm.state import StatesGroup, State


class CreateCar(StatesGroup):
    start_choosing = State()
    brand_choosing = State()
    model_choosing = State()
    motor_choosing = State()
    transmission_choosing = State()
    year_choosing = State()
    yearm_choosing = State()
    cost_choosing = State()
    costm_choosing = State()
    dimension_choosing = State()
    dimensionm_choosing = State()
    show_filter = State()
    add_url_stalk = State()
