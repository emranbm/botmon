import logging
from abc import ABC, abstractmethod
from datetime import time, timedelta

from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone

from main.models import Alert


class AlertSender(ABC):
    def __init__(self):
        self._last_heartbeat_time = timezone.now() - timedelta(seconds=settings.HEARTBEAT_PERIOD_SECONDS)

    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """

        :param alert:
        :return: True if the user is successfully informed. Otherwise False.
        """
        pass

    @abstractmethod
    async def send_alert_fixed(self, alert: Alert) -> bool:
        """

        :param alert:
        :return: True if the user is successfully informed. Otherwise False.
        """
        pass

    @abstractmethod
    async def send_heartbeat_to_admin(self) -> None:
        """
        Sending a heartbeat to someone ensures the monitoring system itself is up and running.
        This method is called periodically. Its period is defined in settings as HEARTBEAT_PERIOD_SECONDS
        """
        pass

    async def send_appropriate_alerts(self):
        alerts = Alert.objects.filter(sent=False).aiterator()
        total_count = 0
        sent_count = 0
        async for alert in alerts:
            total_count += 1
            sent = False
            if alert.is_fixed():
                sent = await self.send_alert_fixed(alert)
            else:
                if alert.created_at <= timezone.now() - timedelta(seconds=settings.ALERT_CERTAINTY_WAIT_SECONDS):
                    sent = await self.send_alert(alert)
            if sent:
                sent_count += 1
                alert.sent = True
                await sync_to_async(alert.save)()
        logging.info(f"Informed {sent_count} alerts (or fixed alerts) out of {total_count}.")
        if (timezone.now() - self._last_heartbeat_time).total_seconds() >= settings.HEARTBEAT_PERIOD_SECONDS:
            await self.send_heartbeat_to_admin()
            self._last_heartbeat_time = timezone.now()
