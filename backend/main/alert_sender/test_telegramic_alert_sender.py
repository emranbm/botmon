from unittest.mock import AsyncMock

from django.test import TestCase
from django.utils import timezone
from telegram.ext import Application

from main import testing_utils
from main.alert_sender.telegramic_alert_sender import TelegramicAlertSender
from main.models import Alert


class TelegramicAlertSenderTest(TestCase):
    @testing_utils.mock_telegram_bot_engine_async
    async def test_should_send_alert(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot)
        await TelegramicAlertSender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_called_once()
        self.assertEqual(user.telegram_chat_id, mocked_send_message.call_args_list[0].kwargs['chat_id'])

    @testing_utils.mock_telegram_bot_engine_async
    async def test_alert_should_contain_appropriate_message(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot)
        await TelegramicAlertSender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        alert_text: str = mocked_send_message.call_args_list[0].kwargs['text']
        self.assertTrue(bot.telegram_username in alert_text)
        self.assertTrue("alert" in alert_text.lower())
        self.assertTrue("down" in alert_text.lower())

    @testing_utils.mock_telegram_bot_engine_async
    async def test_should_not_send_fixed_alert(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot, fixed_at=timezone.now())
        with self.assertRaises(AssertionError):
            await TelegramicAlertSender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_not_called()

    @testing_utils.mock_telegram_bot_engine_async
    async def test_should_not_send_already_sent_alert(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot, sent=True)
        with self.assertRaises(AssertionError):
            await TelegramicAlertSender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_not_called()
