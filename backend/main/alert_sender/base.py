import logging
from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async

from main.models import Alert


class AlertSender(ABC):
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
                sent = await self.send_alert(alert)
            if sent:
                sent_count += 1
                alert.sent = True
                await sync_to_async(alert.save)()
        logging.info(f"Informed {sent_count} alerts (or fixed alerts) out of {total_count}.")
