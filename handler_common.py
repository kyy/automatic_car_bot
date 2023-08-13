import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards import start_menu_kb
from logic.text import TXT
from commands import commands

router = Router()


async def all_commands(allcommands):
    c_list = []
    [(c_list.append(cmd.command)) for cmd in allcommands]
    return "   ".join(c_list)


@router.message(Command(commands=["com"]))
@router.message(Command(commands=["c"]))
@router.message((F.text.casefold() == "com") | F.text.casefold() == "c")
async def cmd_com(message: Message):
    await message.answer(text=TXT['msg_com'].format(all_commands=await all_commands(commands)))


@router.message(Command(commands=["start"]))
@router.message(Command(commands=["s"]))
@router.message((F.text.casefold() == "start") | (F.text.casefold() == "s"))
async def cmd_start(message: Message):
    await message.answer(TXT['info_start_menu'], reply_markup=start_menu_kb(True))


@router.message(Command(commands=["reset"]))
@router.message(Command(commands=["r"]))
@router.message((F.text.casefold() == "reset") | (F.text.casefold() == "r"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state != 'CreateCar:show_filter':
        logging.info("Cancelling state %r", current_state)
        await message.answer("Отмена", reply_markup=ReplyKeyboardRemove())
        await message.answer(TXT['info_start_menu'], reply_markup=start_menu_kb(True))


@router.message(Command(commands=["help"]))
@router.message(Command(commands=["h"]))
@router.message((F.text.casefold() == "help") | (F.text.casefold() == "h"))
async def cmd_help(message: Message):
    c = ''
    for cmd in commands:
        c += f'<b>{cmd.command}</b>\n{cmd.full_description}\n\n'
    await message.answer(c, parse_mode='HTML')
