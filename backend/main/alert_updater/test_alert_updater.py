from typing import Iterable, AsyncIterable, List

from django.test import TestCase
from django.utils import timezone

from main import testing_utils
from main.alert_updater.alert_updater import AlertUpdater
from main.health_checker.health_checker import HealthChecker
from main.models import TargetBot, Alert


class MockedHeathChecker(HealthChecker):
    def __init__(self, unhealthy_bots: Iterable[TargetBot]):
        self._unhealthy_bots = unhealthy_bots

    async def get_unhealthy_bots(self) -> AsyncIterable[TargetBot]:
        for bot in self._unhealthy_bots:
            yield bot


class AlertUpdaterTest(TestCase):
    def setUp(self) -> None:
        self.user, self.bot = testing_utils.create_user_and_their_bot("user", "user_bot")

    async def _update_alerts(self, unhealthy_bots: List[TargetBot]):
        alert_updater = AlertUpdater(MockedHeathChecker(unhealthy_bots=unhealthy_bots))
        await alert_updater.update_alerts()

    async def test_should_save_new_unhealthy_bot_alert(self):
        await self._update_alerts([self.bot])
        self.assertTrue(await Alert.objects.filter(target_bot=self.bot).aexists())

    async def test_should_not_save_redundant_active_alert(self):
        await self._update_alerts([self.bot])
        await self._update_alerts([self.bot])
        self.assertEqual(1, await Alert.objects.filter(target_bot=self.bot).acount())

    async def test_should_save_new_alert_when_non_active_alert_exists(self):
        await Alert.objects.acreate(target_bot=self.bot, fixed_at=timezone.now())
        await self._update_alerts([self.bot])
        self.assertEqual(2, await Alert.objects.filter(target_bot=self.bot).acount())
        self.assertEqual(1, await Alert.objects.filter(target_bot=self.bot, fixed_at=None).acount())
