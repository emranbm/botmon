from datetime import timedelta
from unittest.mock import AsyncMock

from django.test import TestCase, override_settings
from django.utils import timezone
from telegram.ext import Application

from main import testing_utils
from main.alert_sender.telegramic_alert_sender import TelegramicAlertSender
from main.models import Alert


@override_settings(ALERT_CERTAINTY_WAIT_SECONDS=0)
class TelegramicAlertSenderTest(TestCase):
    @staticmethod
    def _get_alert_sender():
        return TelegramicAlertSender(enable_heartbeat=False)

    @testing_utils.mock_telegram_bot_engine_async
    async def test_should_send_alert(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot)
        await self._get_alert_sender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_called_once()
        self.assertEqual(user.telegram_chat_id, mocked_send_message.call_args_list[0].kwargs['chat_id'])

    @testing_utils.mock_telegram_bot_engine_async
    async def test_alert_should_contain_appropriate_message(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot)
        await self._get_alert_sender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        alert_text: str = mocked_send_message.call_args_list[0].kwargs['text']
        self.assertTrue(bot.telegram_username in alert_text)
        self.assertTrue("alert" in alert_text.lower())
        self.assertTrue("down" in alert_text.lower())

    @testing_utils.mock_telegram_bot_engine_async
    async def test_send_alert_method_should_not_send_fixed_alert(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        alert = await Alert.objects.acreate(target_bot=bot, fixed_at=timezone.now())
        with self.assertRaises(AssertionError):
            await self._get_alert_sender().send_alert(alert)
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_not_called()

    @testing_utils.mock_telegram_bot_engine_async
    async def test_send_alert_method_should_send_already_sent_alert_again(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        alert = await Alert.objects.acreate(target_bot=bot, sent=True)
        await self._get_alert_sender().send_alert(alert)
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_called_once()

    @testing_utils.mock_telegram_bot_engine_async
    async def test_already_sent_alerts_should_not_get_sent_again(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot, sent=True)
        await self._get_alert_sender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_not_called()

    @testing_utils.mock_telegram_bot_engine_async
    async def test_should_inform_fixed_alert(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot, fixed_at=timezone.now() + timedelta(seconds=1), sent=False)
        await self._get_alert_sender().send_appropriate_alerts()
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_called_once()
        self.assertTrue("up" in mocked_send_message.call_args_list[0].kwargs['text'].lower())

    @testing_utils.mock_telegram_bot_engine_async
    async def test_send_alert_fixed_method_should_not_send_non_fixed_alert(self, mocked_telegram_app: Application):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        alert = await Alert.objects.acreate(target_bot=bot)
        with self.assertRaises(AssertionError):
            await self._get_alert_sender().send_alert_fixed(alert)
        mocked_send_message: AsyncMock = mocked_telegram_app.bot.send_message
        mocked_send_message.assert_not_called()
