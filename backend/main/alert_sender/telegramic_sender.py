import telegram
from django.template.loader import render_to_string
from main.utils.async_utils import get_model_prop

from main.alert_sender.base import AlertSender
from main.models import Alert
from main.telegrambot.engine import TelegramBotEngine


class TelegramicSender(AlertSender):
    async def send_alert(self, alert: Alert) -> bool:
        app = TelegramBotEngine.create_app()
        target_bot = await get_model_prop(alert, 'target_bot')
        user = await get_model_prop(target_bot, 'creator')

        message = render_to_string('alert_message.html', {'target_bot': target_bot})
        await app.bot.send_message(chat_id=user.telegram_chat_id,
                                   text=message,
                                   parse_mode=telegram.constants.ParseMode.HTML)
        return True
