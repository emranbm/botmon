from unittest.mock import MagicMock

from django.test import TestCase
from telegram.ext import Application

from main import testing_utils
from main.telegrambot.engine import TelegramBotEngine


class TelegramBotEngineTest(TestCase):
    @testing_utils.mock_telegram_bot_engine
    def test_handlers_are_added(self, mocked_telegram_app: Application):
        TelegramBotEngine.run()
        mocked_telegram_app.add_handler.assert_called()
