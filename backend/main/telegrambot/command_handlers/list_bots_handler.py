from django.template.loader import render_to_string
from telegram import Update
from telegram.ext import ContextTypes

from main.models import TargetBot
from main.telegrambot.command_handlers.base import BaseCommandHandler


class ListBotsHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__('listbots')

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        bots = [c async for c in TargetBot.objects.filter(creator__telegram_user_id=update.effective_user.id).aiterator()]
        message = render_to_string('bots_list.html', {'bots': bots})
        await update.message.reply_html(message)
