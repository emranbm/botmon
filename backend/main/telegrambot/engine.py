import prometheus_client
from django.conf import settings
from telegram.ext import ApplicationBuilder, Application

from main.telegrambot.command_handlers.list_bots_handler import ListBotsHandler
from main.telegrambot.command_handlers.start_command_handler import StartCommandHandler
from main.telegrambot.conversation_handlers.addbot_handler import AddBotHandler
from main.telegrambot.conversation_handlers.delbot_handler import DelBotHandler


class TelegramBotEngine:
    @staticmethod
    def create_app() -> Application:
        app_builder = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN)
        proxy_url = settings.TELEGRAM_PROXY_URL
        if proxy_url is not None:
            app_builder = app_builder \
                .proxy_url(proxy_url) \
                .get_updates_proxy_url(proxy_url)
        return app_builder.build()

    @staticmethod
    def run() -> None:
        prometheus_client.start_http_server(settings.TELEGRAMBOT_METRICS_PORT)

        app = TelegramBotEngine.create_app()
        app.add_handler(StartCommandHandler())
        app.add_handler(AddBotHandler(), 1)
        app.add_handler(DelBotHandler(), 2)
        app.add_handler(ListBotsHandler())
        app.run_polling(drop_pending_updates=True)
