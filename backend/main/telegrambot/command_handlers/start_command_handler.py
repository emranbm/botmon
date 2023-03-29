from django.template.loader import render_to_string
from telegram import Update
from telegram.ext import ContextTypes

from main.telegrambot import utils
from main.telegrambot.command_handlers.base import BaseCommandHandler


class StartCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__('start')

    # Override
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await utils.create_or_update_user(update)
        message = render_to_string('start_command_reply.html', {'update': update})
        await update.message.reply_html(message)
