from unittest.mock import AsyncMock

from django.test import TestCase, override_settings
from django.utils import timezone

from main import testing_utils
from main.alert_sender.base import AlertSender
from main.models import Alert


class AlertSenderImpl(AlertSender):
    async def send_alert(self, alert: Alert) -> bool:
        pass

    async def send_alert_fixed(self, alert: Alert) -> bool:
        pass

    async def send_heartbeat_to_admin(self, message: str):
        pass


@override_settings(ALERT_CERTAINTY_WAIT_SECONDS=0)
class AlertSenderTest(TestCase):
    def setUp(self) -> None:
        self.alert_sender = AlertSenderImpl()
        self.alert_sender.send_alert = AsyncMock()
        self.alert_sender.send_alert_fixed = AsyncMock()
        self.alert_sender.send_heartbeat_to_admin = AsyncMock()

    async def test_should_send_new_alerts_as_active_alerts(self):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot)
        await self.alert_sender.send_appropriate_alerts()
        mocked_send_alert: AsyncMock = self.alert_sender.send_alert
        mocked_send_alert.assert_called_once()
        mocked_send_alert_fixed: AsyncMock = self.alert_sender.send_alert_fixed
        mocked_send_alert_fixed.assert_not_called()

    async def test_should_send_fixed_alerts_as_fixed(self):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot, fixed_at=timezone.now())
        await self.alert_sender.send_appropriate_alerts()
        mocked_send_alert_fixed: AsyncMock = self.alert_sender.send_alert_fixed
        mocked_send_alert_fixed.assert_called_once()
        mocked_send_alert: AsyncMock = self.alert_sender.send_alert
        mocked_send_alert.assert_not_called()

    async def test_should_not_send_already_sent_alerts(self):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot, sent=True)
        await self.alert_sender.send_appropriate_alerts()
        mocked_send_alert: AsyncMock = self.alert_sender.send_alert
        mocked_send_alert.assert_not_called()

    @override_settings(ALERT_CERTAINTY_WAIT_SECONDS=1)
    async def test_should_not_send_new_alert_before_certainty_period(self):
        user, bot = await testing_utils.create_user_and_their_bot_async()
        await Alert.objects.acreate(target_bot=bot)
        await self.alert_sender.send_appropriate_alerts()
        mocked_send_alert: AsyncMock = self.alert_sender.send_alert
        mocked_send_alert.assert_not_called()
