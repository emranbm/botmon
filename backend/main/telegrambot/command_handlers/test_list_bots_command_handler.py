from main import testing_utils

from main.telegrambot.command_handlers.base import BaseCommandHandler
from main.telegrambot.command_handlers.list_bots_handler import ListBotsHandler
from main.telegrambot.command_handlers.test_base_test_case import CommandHandlerBaseTestCase


class ListBotsCommandHandlerTest(CommandHandlerBaseTestCase):
    def get_handler(self) -> BaseCommandHandler:
        return ListBotsHandler()

    async def test_should_promote_addbot_command_when_no_bot_exists(self):
        resp = await self.trigger_handler()
        self.assertTrue("/addbot" in resp)

    async def test_should_show_saved_bot(self):
        user, _ = await testing_utils.create_user_and_their_bot_async("me", "my_bot")
        update = testing_utils.create_default_update(user)
        resp = await self.trigger_handler(update)
        self.assertTrue("@my_bot" in resp)

    async def test_should_not_show_others_bots(self):
        user1, _ = await testing_utils.create_user_and_their_bot_async("me", "my_bot")
        await testing_utils.create_user_and_their_bot_async("someone_else", "his_bot")
        update = testing_utils.create_default_update(user1)
        resp = await self.trigger_handler(update)
        self.assertTrue("@my_bot" in resp)
        self.assertFalse("@his_bot" in resp)
