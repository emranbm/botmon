from abc import ABC, abstractmethod

from main.models import Alert


class AlertSender(ABC):
    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """

        :param alert:
        :return: True if the users are successfully informed. Otherwise False.
        """
        pass
