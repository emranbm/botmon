from random import randint
from typing import Optional
from unittest.mock import Mock, AsyncMock, patch

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes, Application

from main import models
from main.models import User, TargetBot
from main.telegrambot.engine import TelegramBotEngine

TEST_USER_ID = 123
TEST_CHAT_ID = 456
TEST_USER_USERNAME = 'test_username'
TEST_USER_FIRST_NAME = 'first name'
TEST_USER_LAST_NAME = 'last name'


def create_test_user():
    return models.User.objects.create_user("internal_username",
                                           telegram_user_id=TEST_USER_ID,
                                           telegram_username=TEST_USER_USERNAME,
                                           telegram_chat_id=TEST_CHAT_ID,
                                           first_name=TEST_USER_FIRST_NAME + " (custom)",
                                           last_name=TEST_USER_LAST_NAME + " (custom)")


async def create_test_user_async() -> User:
    return await sync_to_async(create_test_user)()


def create_user_and_their_bot(self_telegram_username: str, bot_telegram_username: str) -> User:
    user = User.objects.create_user(f"{self_telegram_username}_local",
                                    telegram_username=self_telegram_username,
                                    telegram_user_id=randint(1, 1000000000000),
                                    telegram_chat_id=randint(1, 1000000000000),
                                    )
    TargetBot(creator=user, telegram_username=bot_telegram_username).save()
    return user


async def create_user_and_their_bot_async(self_telegram_username: str, bot_telegram_username: str) -> User:
    return await sync_to_async(create_user_and_their_bot)(self_telegram_username, bot_telegram_username)


def create_default_update(user: Optional[User] = None) -> Update:
    update: Update = Mock()
    if user is None:
        update.effective_user.id = TEST_USER_ID
        update.effective_user.username = TEST_USER_USERNAME
        update.effective_user.first_name = TEST_USER_FIRST_NAME
        update.effective_user.last_name = TEST_USER_LAST_NAME
        update.effective_chat.id = TEST_CHAT_ID
    else:
        update.effective_user.id = user.telegram_user_id
        update.effective_user.username = user.telegram_username
        update.effective_user.first_name = user.first_name
        update.effective_user.last_name = user.last_name
        update.effective_chat.id = user.telegram_chat_id
    update.message.reply_text = AsyncMock()
    update.message.reply_html = AsyncMock()
    return update


def create_default_context() -> ContextTypes.DEFAULT_TYPE:
    context: ContextTypes.DEFAULT_TYPE = Mock()
    context.bot.send_message = AsyncMock()
    return context


def mock_telegram_bot_engine_async(func):
    async def f(self, create_app_mock):
        app: Application = Mock()
        app.bot.send_message = AsyncMock()
        create_app_mock.return_value = app
        await func(self, app)

    return patch.object(TelegramBotEngine, 'create_app')(f)


def mock_telegram_bot_engine(func):
    def f(self, create_app_mock):
        app: Application = Mock()
        app.bot.send_message = Mock()
        create_app_mock.return_value = app
        func(self, app)

    return patch.object(TelegramBotEngine, 'create_app')(f)
