import random
import string
from datetime import timedelta, datetime
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class _AutoCleanedModel(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_cleaned = False

    class Meta:
        abstract = True

    def clean(self):
        self.is_cleaned = True
        super().clean()

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.full_clean()
        super().save(*args, **kwargs)


class Contactable(_AutoCleanedModel):
    """
    Different ways of contacting someone is aggregated in this mixin.
    """
    telegram_username = models.CharField(null=False, blank=True, default='', max_length=32)

    class Meta:
        abstract = True


class User(AbstractUser, Contactable):
    first_name = models.CharField(null=False, blank=True, default='', max_length=64)
    last_name = models.CharField(null=False, blank=True, default='', max_length=64)
    telegram_user_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)

    @staticmethod
    def generate_random_username() -> str:
        return ''.join(random.choice(string.ascii_letters) for i in range(64))


class TargetBot(Contactable):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            # Should be checked differently whenever contact points other than Telegram are also supported.
            models.UniqueConstraint(fields=['creator', 'telegram_username'], name="duplicate_bot_preventer")
        ]


class Alert(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    fixed_at = models.DateTimeField(null=True)
    target_bot = models.ForeignKey(TargetBot, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)

    def is_fixed(self) -> bool:
        return self.fixed_at is not None

    def has_passed_certainty_waiting_period(self, current_time: Optional[datetime] = None):
        """
        Determines whether the alert is fully active (i.e. has waited for certainty period and has not fixed yet) or not.
        :param current_time: The current time to evaluate the alert age.
        :return: True if the alert age has passed the certainty waiting period (and hence should be informed). Otherwise False.
        """
        return (current_time or timezone.now()) - self.created_at >= timedelta(seconds=settings.ALERT_CERTAINTY_WAIT_SECONDS)
