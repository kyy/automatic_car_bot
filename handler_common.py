import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from commands import commands
from keyboards import start_menu_kb, donate_kb, asky_kb
from logic.text import TXT

router = Router()


async def all_commands(allcommands):
    c_list = []
    [(c_list.append(cmd.command)) for cmd in allcommands]
    return "   ".join(c_list)


@router.message(Command(commands=["start"]))
@router.message(Command(commands=["s"]))
@router.message((F.text.casefold() == "start") | (F.text.casefold() == "s"))
async def cmd_start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "CreateCar:show_filter":
        logging.info("Cancelling state %r", current_state)
        await state.set_state(None)
        await state.clear()
        await message.answer(TXT["info_start_menu"], reply_markup=start_menu_kb(True))
    elif current_state == "CreateCar:show_filter":
        await message.answer(TXT["msg_reset_error"], reply_markup=ReplyKeyboardRemove())


@router.message(Command(commands=["help"]))
@router.message(Command(commands=["h"]))
@router.message((F.text.casefold() == "help") | (F.text.casefold() == "h"))
async def cmd_help(message: Message):
    c = ""
    for cmd in commands:
        c += f"<b>{cmd.command}     {cmd.description}</b>\n{cmd.full_description}\n\n"
    await message.answer(c, parse_mode="HTML")


@router.message(Command(commands=["donate"]))
@router.message(Command(commands=["d"]))
@router.message((F.text.casefold() == "donate") | (F.text.casefold() == "d"))
async def cmd_help(message: Message):
    await message.answer(TXT['info_donate'], parse_mode="HTML", reply_markup=donate_kb())


@router.message(Command(commands=["tell"]))
@router.message(Command(commands=["t"]))
@router.message((F.text.casefold() == "tell") | (F.text.casefold() == "t"))
async def cmd_help(message: Message):
    await message.answer(TXT['info_asky'], parse_mode="HTML", reply_markup=asky_kb())
