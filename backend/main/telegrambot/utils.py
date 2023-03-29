import telegram
from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password

from main import models


async def create_or_update_user(update: telegram.Update) -> models.User:
    (user, created) = await models.User.objects.aget_or_create(
        telegram_user_id=update.effective_user.id,
        defaults={
            'telegram_chat_id': update.effective_chat.id,
            'telegram_username': update.effective_user.username,
            'username': models.User.generate_random_username(),
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name or '',
            'password': make_password(None),
        })
    if not created:
        await _update_user_if_needed(user, update)
    return user


async def _update_user_if_needed(user: models.User, update: telegram.Update) -> None:
    should_save = False
    if user.telegram_username != update.effective_user.username:
        user.telegram_username = update.effective_user.username
        should_save = True
    if user.telegram_chat_id != update.effective_chat.id:
        user.telegram_chat_id = update.effective_chat.id
        should_save = True
    if should_save:
        await sync_to_async(user.save)()
