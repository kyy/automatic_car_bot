from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.utils.callback_answer import CallbackAnswer
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import CallbackQuery, Message, TelegramObject


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")
        bot = data["bot"]
        # Если такого флага на хэндлере нет
        if not long_operation_type:
            return await handler(event, data)

        # Если флаг есть
        async with ChatActionSender(
            bot=bot,
            action=long_operation_type,
            chat_id=event.from_user.id
        ):
            return await handler(event, data)

