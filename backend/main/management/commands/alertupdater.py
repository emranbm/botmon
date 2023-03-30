import asyncio
from argparse import ArgumentParser

from django.core.management import BaseCommand

from main.alert_updater.alert_updater import AlertUpdater
from main.health_checker.health_checker import HealthChecker


class Command(BaseCommand):
    help = 'Checks target bots healths and saves corresponding alerts'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--period', action='store',
                            help="Waiting period between checks. (seconds)",
                            type=int,
                            default=60)

    def handle(self, *args, **options):
        period_seconds = options['period']
        self.stdout.write(f"Running the health checks every {period_seconds} seconds ...")
        alert_updater = AlertUpdater(HealthChecker())
        while True:
            asyncio.run(alert_updater.update_alerts())
            asyncio.sleep(period_seconds)
