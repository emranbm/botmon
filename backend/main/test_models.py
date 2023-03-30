from django.test import TestCase
from django.utils import timezone

from main import testing_utils
from main.models import Alert


class AlertTest(TestCase):
    def test_should_be_non_fixed_by_default(self):
        user, bot = testing_utils.create_user_and_their_bot()
        alert = Alert.objects.create(target_bot=bot)
        self.assertFalse(alert.is_fixed())

    def test_should_be_non_sent_by_default(self):
        user, bot = testing_utils.create_user_and_their_bot()
        alert = Alert.objects.create(target_bot=bot)
        self.assertFalse(alert.sent)

    def test_should_gets_fixed_when_fixed_at_is_set(self):
        user, bot = testing_utils.create_user_and_their_bot()
        alert = Alert.objects.create(target_bot=bot)
        self.assertFalse(alert.is_fixed())
        alert.fixed_at = timezone.now()
        self.assertTrue(alert.is_fixed())

