from django.test import TestCase

from main import testing_utils
from main.models import TargetBot
from main.telegrambot.conversation_handlers.addbot_handler import AddBotHandler


class AddBotHandlerTest(TestCase):
    def setUp(self) -> None:
        self.user = testing_utils.create_test_user()

    async def test_bot_should_be_saved(self):
        update = testing_utils.create_default_update()
        context = testing_utils.create_default_context()
        update.message.text = "@my_bot"
        await AddBotHandler()._on_bot_username_entered(update, context)
        self.assertTrue(await TargetBot.objects.filter(creator=self.user, telegram_username="my_bot").aexists(),
                        "TargetBot not found in database!")

    async def test_should_send_appropriate_message_on_duplicate_bot(self):
        await TargetBot.objects.acreate(creator=self.user, telegram_username="my_bot")
        update = testing_utils.create_default_update()
        context = testing_utils.create_default_context()
        update.message.text = "@my_bot"
        await AddBotHandler()._on_bot_username_entered(update, context)
        self.assertTrue("already" in update.message.reply_html.call_args.args[0].lower())
