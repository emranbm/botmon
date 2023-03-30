from django.core.exceptions import SynchronousOnlyOperation
from django.test import TestCase

from main import testing_utils
from main.models import TargetBot
from main.utils.async_utils import get_model_prop


class GetModelPropTest(TestCase):
    async def test_can_get_lazy_loaded_relation_on_async_context(self):
        await testing_utils.create_user_and_their_bot_async("user", "bot")
        target_bot = await TargetBot.objects.afirst()
        with self.assertRaises(SynchronousOnlyOperation):
            _ = target_bot.creator
        self.assertIsNotNone(await get_model_prop(target_bot, 'creator'))
