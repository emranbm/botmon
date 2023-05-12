from datetime import timedelta

from django.test import TestCase, override_settings
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

    @override_settings(ALERT_CERTAINTY_WAIT_SECONDS=0)
    def test_method_has_passed_certainty_period_returns_true_when_certainty_period_is_0(self):
        user, bot = testing_utils.create_user_and_their_bot()
        alert = Alert.objects.create(target_bot=bot)
        self.assertTrue(alert.has_passed_certainty_waiting_period())

    @override_settings(ALERT_CERTAINTY_WAIT_SECONDS=100)
    def test_method_has_passed_certainty_period_returns_false_when_certainty_period_is_large_enough(self):
        user, bot = testing_utils.create_user_and_their_bot()
        alert = Alert.objects.create(target_bot=bot)
        self.assertFalse(alert.has_passed_certainty_waiting_period())

    @override_settings(ALERT_CERTAINTY_WAIT_SECONDS=100)
    def test_method_has_passed_certainty_period_returns_appropriately_with_custom_current_time(self):
        user, bot = testing_utils.create_user_and_their_bot()
        alert = Alert.objects.create(target_bot=bot)
        self.assertFalse(alert.has_passed_certainty_waiting_period(current_time=timezone.now() + timedelta(seconds=5)))
        self.assertTrue(alert.has_passed_certainty_waiting_period(current_time=timezone.now() + timedelta(seconds=200)))
