from abc import ABC, abstractmethod
from typing import Optional

from django.test import TestCase
from telegram import Update
from telegram.ext import ContextTypes

from main import testing_utils
from main.telegrambot.command_handlers.command_handler_with_metrics import CommandHandlerWithMetrics

from main.telegrambot.command_handlers.base import BaseCommandHandler


class CommandHandlerBaseTestCase(TestCase, ABC):
    @abstractmethod
    def get_handler(self) -> BaseCommandHandler:
        pass

    async def trigger_handler(self, update: Optional[Update] = None, context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> str:
        if update is None:
            update = testing_utils.create_default_update()
        if context is None:
            context = testing_utils.create_default_context()
        await self.get_handler().handle_command(update, context)
        response_message = update.message.reply_html.call_args.args[0]
        return response_message
