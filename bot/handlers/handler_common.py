import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.commands import commands
from bot.keyboards import start_menu_kb, donate_kb, asky_kb

from logic.database.config import database
from logic.text import TXT

router = Router()


@router.message(Command(commands=["start"]))
@router.message(Command(commands=["s"]))
@router.message((F.text.casefold() == "start") | (F.text.casefold() == "s"))
async def cmd_start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await state.clear()
    logging.info("Cancelling state %r", current_state)
    await message.answer(TXT["info_start_menu"], reply_markup=await start_menu_kb(True, message))

    text = message.text
    ref_id = int(message.text.split(' ')[1]) if len(text.split()) > 1 else None
    tel_id = message.from_user.id

    async with database() as db:
        check_id_cursor = await db.execute("SELECT tel_id FROM user WHERE tel_id = $s", (tel_id,))
        check_id = await check_id_cursor.fetchone()
        if check_id is None:
            await db.execute(
                "INSERT INTO user (tel_id) VALUES ($s)", (tel_id,))
            logging.info("Added new user %r", tel_id)
        elif ref_id:
            await db.execute("UPDATE user SET ref = ref + 1 WHERE tel_id = $s", (ref_id,))
            logging.info("Reffered by %r", ref_id)

        await db.commit()


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
    tel_id = message.from_user.id
    async with database() as db:
        ref_cursor = await db.execute("""SELECT ref FROM user WHERE tel_id = $s""", (tel_id,))
        ref = await ref_cursor.fetchone()
        ref = ref[0]
    await message.answer(
        TXT['info_asky'].format(tel_id=tel_id, ref=ref),
        parse_mode="HTML",
        reply_markup=asky_kb(tel_id))
