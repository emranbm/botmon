from datetime import datetime
from enum import Enum

from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, ContextTypes, MessageHandler, filters

from main.models import TargetBot
from main.telegrambot import utils


class _State(Enum):
    START = 0
    RECEIVE_USERNAME = 1


class DelBotHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
            entry_points=[CommandHandler('delbot', self._on_delcruch)],
            states={
                _State.RECEIVE_USERNAME: [
                    MessageHandler(filters.Regex("^@.*_bot$"), self._on_bot_username_entered),
                    MessageHandler(filters.ALL & (~filters.COMMAND), self._on_wrong_username_format),
                ]
            },
            fallbacks=[MessageHandler(filters.COMMAND, self._on_cancel)], )

    @staticmethod
    async def _on_delcruch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> _State:
        await update.message.reply_text("Send the username to delete.\n"
                                        "Or /cancel.")
        return _State.RECEIVE_USERNAME

    @staticmethod
    async def _on_wrong_username_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> _State:
        await update.message.reply_text("Please send the username in the form of @username_bot\n"
                                        "Or /cancel")
        return _State.RECEIVE_USERNAME

    @staticmethod
    async def _on_bot_username_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> _State:
        user = await utils.create_or_update_user(update)
        bot_username = update.message.text
        try:
            target_bot = await TargetBot.objects.aget(creator=user, telegram_username=bot_username.lstrip("@"))
            await sync_to_async(target_bot.delete)()
        except TargetBot.DoesNotExist:
            await update.message.reply_text("Username not found in the bots list! Please check and try again.")
        except Exception:
            message = render_to_string('unexpected_error.html')
            await update.message.reply_html(message)
        else:
            message = render_to_string('bot_deleted_ack.html', {'bot_username': bot_username})
            await update.message.reply_html(message)
        return ConversationHandler.END

    @staticmethod
    async def _on_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> _State:
        await update.message.reply_text("'delbot' operation canceled!")
        return ConversationHandler.END
