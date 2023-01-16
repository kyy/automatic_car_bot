import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand
from aiogram.filters import Command, Text


router = Router()


@router.message(Command(commands=["start"]))
@router.message(F.text.casefold() == "start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=f"Привет, {message.from_user.full_name}!"
             "\nЭто бот может искать объявления автомобилей."
             "\nНачать - /car.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await message.answer(
        "Отмена",
        reply_markup=ReplyKeyboardRemove(),
    )\

@router.message(Command(commands=["clear"]))
@router.message(F.text.casefold() == "clear")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Отмена и сброс фильтра",
        reply_markup=ReplyKeyboardRemove(),
    )

