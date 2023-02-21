import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand
from aiogram.filters import Command, CommandObject


router = Router()


commands = [
        BotCommand(
            command="car",
            description="Создать новый фильтр",
            full_description='Пошаговый помощник, поможет вам сгенерировать фильтр для поиска объявлений.\n'
                             'Фильтр можно редактировать как сообщение и отправлять в любой момент.'
        ),
        BotCommand(
            command='show',
            description='Отобразить текущий фильтр ',
            full_description='Отобразит сформированный фильтр в виде кнопки.\n'
                             'Можно применить в любой момент, позволит пропустить шаги помощника.'
        ),

        BotCommand(
            command="cancel",
            description="Прервать действие",
            full_description='Отменит текущее действие.\n'
                             'Не затрагивает данные фильтра'
        ),
        BotCommand(
            command="clear",
            description="Прервать и очистить фильтр",
            full_description='Отмена текущего действия.\n'
                             'Удаляет текущий фильтр.'
        ),
        BotCommand(
            command="help",
            description="Помощь",
            full_description='Дополнительная вспомогательная инструкция.'
        ),
]


async def set_commands(bot: Bot):
    await bot.set_my_commands(commands)


@router.message(Command(commands=["help"]))
@router.message(F.text.startswith == "help")
async def cmd_help(message: Message, command: CommandObject):
    if command.args:
        for cmd in commands:
            if cmd.command == command.args:
                return await message.answer(
                    f'{cmd.command} - {cmd.full_description}'
                )
        else:
            return await message.answer('Команда не найдена')
    await message.answer(
        text=f"Для получение подробного описание команд наберите:"
             "\n/help <имя команды>"
    )


@router.message(Command(commands=["start"]))
@router.message(F.text.casefold() == "start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=f"Привет, {message.from_user.full_name}!"
             "\nЭто бот может искать объявления автомобилей."
             "\nНачать - /car."
             "\nПомощь - /help.",
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
    )


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
