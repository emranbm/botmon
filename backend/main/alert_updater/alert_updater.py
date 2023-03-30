from datetime import datetime

from asgiref.sync import sync_to_async

from main.health_checker.health_checker import HealthChecker
from main.models import Alert


class AlertUpdater:
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker

    async def update_alerts(self):
        now = datetime.now()
        unhealthy_bots = self.health_checker.get_unhealthy_bots()
        unhealthy_bot_ids = []
        async for bot in unhealthy_bots:
            unhealthy_bot_ids.append(bot.pk)
            active_alert_already_exist = await Alert.objects.filter(target_bot=bot, fixed_at=None).aexists()
            if not active_alert_already_exist:
                await Alert.objects.acreate(target_bot=bot)
        fixed_alerts = Alert.objects.exclude(target_bot_id__in=unhealthy_bot_ids).filter(fixed_at=None).aiterator()
        async for alert in fixed_alerts:
            alert.fixed_at = now
            await sync_to_async(alert.save)()
