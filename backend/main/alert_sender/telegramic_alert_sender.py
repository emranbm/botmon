import telegram
from django.template.loader import render_to_string
from main.utils.async_utils import get_model_prop

from main.alert_sender.base import AlertSender
from main.models import Alert
from main.telegrambot.engine import TelegramBotEngine


class TelegramicAlertSender(AlertSender):
    async def send_alert(self, alert: Alert) -> bool:
        if alert.is_fixed():
            raise AssertionError("Alert is fixed!")
        return await self._send_message_for_alert(alert, 'alert_active_message.html')

    async def send_alert_fixed(self, alert: Alert) -> bool:
        if not alert.is_fixed():
            raise AssertionError("Alert is not fixed!")
        return await self._send_message_for_alert(alert, 'alert_fixed_message.html')

    @staticmethod
    async def _send_message_for_alert(alert: Alert, message_template: str) -> bool:
        app = TelegramBotEngine.create_app()
        target_bot = await get_model_prop(alert, 'target_bot')
        user = await get_model_prop(target_bot, 'creator')

        message = render_to_string(message_template, {'target_bot': target_bot})
        await app.bot.send_message(chat_id=user.telegram_chat_id,
                                   text=message,
                                   parse_mode=telegram.constants.ParseMode.HTML)
        return True
