import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models


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
