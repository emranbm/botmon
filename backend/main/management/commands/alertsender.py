import asyncio
from argparse import ArgumentParser
from time import sleep

from django.core.management import BaseCommand

from main.alert_sender.telegramic_alert_sender import TelegramicAlertSender
from main.alert_updater.alert_updater import AlertUpdater
from main.health_checker.health_checker import HealthChecker


class Command(BaseCommand):
    help = 'Sends new non-fixed alerts'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--period', action='store',
                            help="Waiting period between checks. (seconds)",
                            type=int,
                            default=60)

    def handle(self, *args, **options):
        period_seconds = options['period']
        self.stdout.write(f"Sending new alerts every {period_seconds} seconds ...")
        alert_sender = TelegramicAlertSender()
        while True:
            asyncio.run(alert_sender.send_appropriate_alerts())
            sleep(period_seconds)
