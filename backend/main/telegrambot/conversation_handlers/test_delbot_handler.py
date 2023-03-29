from django.test import TestCase

from main import testing_utils
from main.models import TargetBot
from main.telegrambot.conversation_handlers.delbot_handler import DelBotHandler


class DelBotHandlerTest(TestCase):
    def setUp(self) -> None:
        self.user = testing_utils.create_test_user()

    async def test_bot_should_get_deleted(self):
        TargetBot.objects.acreate(creator=self.user, telegram_username="my_bot")
        update = testing_utils.create_default_update()
        context = testing_utils.create_default_context()
        update.message.text = "@my_bot"
        await DelBotHandler()._on_bot_username_entered(update, context)
        self.assertFalse(await TargetBot.objects.filter(creator=self.user, telegram_username="my_bot").aexists(),
                         "The bot found in database!")
