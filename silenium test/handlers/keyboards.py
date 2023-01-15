from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def single_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def multi_row_keyboard(items: list[str], columns: int = 4, **kwargs) -> ReplyKeyboardMarkup:
    return ReplyKeyboardBuilder().row(*[KeyboardButton(text=item) for item in items]).adjust(columns).as_markup(**kwargs)
