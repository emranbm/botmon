import asyncio
from asyncio import sleep
from contextlib import asynccontextmanager
from typing import List, AsyncIterable, Optional
from urllib.parse import urlparse

import socks
from django.conf import settings
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation

from main.models import TargetBot


class HealthChecker:
    async def get_unhealthy_bots(self) -> AsyncIterable[TargetBot]:
        target_bots: AsyncIterable[TargetBot] = TargetBot.objects.aiterator()
        async with self._create_telegram_client() as telegram_client:
            async for target_bot in target_bots:
                async with self._create_conversation(target_bot.telegram_username, telegram_client) as conv:
                    conv: Conversation
                    await conv.send_message(settings.TELEGRAM_AGENT_HEALTH_CHECK_MESSAGE)
                    try:
                        await conv.get_response(timeout=settings.TELEGRAM_AGENT_HEALTH_CHECK_TIMEOUT_SECONDS)
                    except asyncio.TimeoutError:
                        yield target_bot

    @asynccontextmanager
    async def _create_telegram_client(self) -> TelegramClient:
        telegram_client = TelegramClient(
            StringSession(settings.TELEGRAM_AGENT_SESSION_STRING),
            settings.TELEGRAM_AGENT_API_ID,
            settings.TELEGRAM_AGENT_API_HASH,
            sequential_updates=True,
        )
        proxy_url = settings.TELEGRAM_PROXY_URL
        if proxy_url is not None:
            u = urlparse(proxy_url)
            assert u.scheme == "socks5", "Currently, just socks5 protocol is supported for proxy"
            telegram_client.set_proxy((socks.PROXY_TYPE_SOCKS5, u.hostname, u.port or 80))
        await telegram_client.connect()
        await telegram_client.get_me()
        await telegram_client.get_dialogs()

        yield telegram_client

        await telegram_client.disconnect()
        await telegram_client.disconnected

    @asynccontextmanager
    async def _create_conversation(self, username: str, telegram_client: TelegramClient) -> Conversation:
        conversation_context_manager = telegram_client.conversation(username, timeout=10)
        conversation = await conversation_context_manager.__aenter__()
        await sleep(0.5)  # A hack recommended at https://shallowdepth.online/posts/2021/12/end-to-end-tests-for-telegram-bots/

        yield conversation

        await conversation_context_manager.__aexit__(None, None, None)
