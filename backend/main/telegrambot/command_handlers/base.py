from abc import abstractmethod, ABC
from typing import Optional, Callable, Awaitable

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


class BaseCommandHandler(CommandHandler, ABC):
    command: str

    def __init__(self, command: str, handler: Optional[Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]] = None):
        super().__init__(command, self.handle_command)
        self.command = command
        self._passed_handler = handler

    @abstractmethod
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass
