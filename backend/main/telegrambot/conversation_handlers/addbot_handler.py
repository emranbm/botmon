from enum import Enum

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, ContextTypes, MessageHandler, filters

from main.models import TargetBot
from main.telegrambot import utils


class _State(Enum):
    START = 0
    RECEIVE_USERNAME = 1


class AddBotHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
            entry_points=[CommandHandler('addbot', self._on_addcruch)],
            states={
                _State.RECEIVE_USERNAME: [
                    MessageHandler(filters.Regex("^@.*_bot$"), self._on_bot_username_entered),
                    MessageHandler(filters.ALL & (~filters.COMMAND), self._on_wrong_username_format),
                ]
            },
            fallbacks=[MessageHandler(filters.COMMAND, self._on_cancel)], )

    @staticmethod
    async def _on_addcruch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> _State:
        await update.message.reply_text("OK! Please send me your bot's username.\n"
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
            await TargetBot.objects.acreate(creator=user, telegram_username=bot_username.lstrip("@"))
        except ValidationError:
            message = render_to_string('duplicate_add_bot_error.html')
            await update.message.reply_html(message)
        except Exception:
            message = render_to_string('unexpected_error.html')
            await update.message.reply_html(message)
        else:
            message = render_to_string('target_bot_saved_ack.html')
            await update.message.reply_html(message)
        return ConversationHandler.END

    @staticmethod
    async def _on_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> _State:
        await update.message.reply_text("'addbot' operation canceled!")
        return ConversationHandler.END
