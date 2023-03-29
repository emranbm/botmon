from django.core.management import BaseCommand

from main.telegrambot.engine import TelegramBotEngine


class Command(BaseCommand):
    help = 'Manages Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write("Running the bot...")
        TelegramBotEngine.run()
