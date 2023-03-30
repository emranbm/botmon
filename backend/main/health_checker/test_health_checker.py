import asyncio
from unittest.mock import patch, MagicMock

from django.test import TestCase
from telethon.tl.custom import Conversation

from main import testing_utils
from main.health_checker.health_checker import HealthChecker


def _patch_telegram_client(test_func):
    @patch('main.health_checker.health_checker.HealthChecker._create_telegram_client', MagicMock())
    @patch('main.health_checker.health_checker.HealthChecker._create_conversation')
    async def func(self, create_conversation_mock: MagicMock):
        conversation = create_conversation_mock.return_value.__aenter__.return_value
        await test_func(self, conversation)

    return func


class HealthCheckerTest(TestCase):
    @_patch_telegram_client
    async def test_should_detect_unhealthy_bot(self, conversation: Conversation):
        await testing_utils.create_user_and_their_bot_async("user", "bot")
        health_checker = HealthChecker()
        conversation.get_response.side_effect = asyncio.TimeoutError()
        unhealthy_bots = [b async for b in health_checker.get_unhealthy_bots()]
        self.assertEqual(1, len(unhealthy_bots))

    @_patch_telegram_client
    async def test_should_not_return_healthy_bot(self, conversation: Conversation):
        await testing_utils.create_user_and_their_bot_async("user", "bot")
        health_checker = HealthChecker()
        unhealthy_bots = [b async for b in health_checker.get_unhealthy_bots()]
        self.assertEqual(0, len(unhealthy_bots))
