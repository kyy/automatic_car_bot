import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand
from aiogram.filters import Command, CommandObject
from keyboards import start_menu_with_help
from classes import bot


router = Router()


commands = [
        BotCommand(
            command="start",
            description="Управление фильтрами",
            full_description='Меню управления фильтрами.\n'
                             'Создание, редактирование задач, удаление.'
        ),

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


def all_commands(allcommands):
    c_list = []
    [(c_list.append(str(cmd.command))) for cmd in allcommands]
    return ", ".join(c_list)


async def set_commands(bot_: bot):
    await bot_.set_my_commands(commands)


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, command: CommandObject):
    if command.args:
        for cmd in commands:
            if cmd.command == command.args:
                return await message.answer(
                    f'{cmd.command} - {cmd.full_description}'

                )
        else:
            return await message.answer('Команда не найдена'
                                        '\nДоступные команды:'
                                        f'\n{all_commands(commands)}')
    await message.answer(
        text=f"Для получение подробного описание команд наберите:"
             "\n/help <имя команды>"
             "\nДоступные команды:"
             f"\n{all_commands(commands)}"
    )


@router.message(Command(commands=["start"]))
@router.message(F.text.casefold() == "start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Главное меню', reply_markup=start_menu_with_help(True))


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
