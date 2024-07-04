from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone
from .models import CallSchedule
from .tasks import check_scheduled_call_task
from datetime import timedelta
from pytz import timezone as pytz_timezone

from ..accounts.models import CustomUser, GiftReceiver


class CheckScheduledCallTaskTest(TestCase):

    @patch('agent.apps.call_schedules.tasks.print')
    def test_task_identifies_recurring_call(self, mock_print):
        # Create a gift receiver
        user = CustomUser.objects.create(email='kai+00011@meetbeagle.com', is_receiver=True, is_giver=False)
        gift_receiver = GiftReceiver.objects.filter(user=user).first()
        # Setup
        now = timezone.now()

        # Daily Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=1, hours=23, minutes=50),
            frequency_unit="DAY",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Daily Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=0, hours=23, minutes=50),
            frequency_unit="DAY",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Daily Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=0, hours=23, minutes=30),
            frequency_unit="DAY",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Daily Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=0, hours=0, minutes=-30),
            frequency_unit="DAY",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Daily Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=0, hours=0, minutes=-10),
            frequency_unit="DAY",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Daily Call to be NOT executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=0, hours=0, minutes=0),
            frequency_unit="DAY",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=1, days=6, hours=23, minutes=30),
            frequency_unit="WEEK",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=0, days=0, hours=0, minutes=-30),
            frequency_unit="WEEK",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=0, days=0, hours=0, minutes=-10),
            frequency_unit="WEEK",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Weekly Call to be NOT executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=0, days=0, hours=0, minutes=0),
            frequency_unit="WEEK",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Weekly Call to be NOT executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=2, days=0, hours=0, minutes=0),
            frequency_unit="WEEK",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Weekly Call to be NOT executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=1, days=6, hours=23, minutes=0),
            frequency_unit="WEEK",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=1, days=6, hours=23, minutes=50),
            frequency_unit="WEEK",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Bi Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=1, days=6, hours=23, minutes=50),
            frequency_unit="WEEK",
            frequency_interval=2,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Bi Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=0, days=0, hours=0, minutes=-30),
            frequency_unit="WEEK",
            frequency_interval=2,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Bi Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=0, days=0, hours=0, minutes=-10),
            frequency_unit="WEEK",
            frequency_interval=2,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Bi Weekly Call to be NOT executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=0, days=0, hours=0, minutes=0),
            frequency_unit="WEEK",
            frequency_interval=2,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Bi Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=1, days=6, hours=23, minutes=30),
            frequency_unit="WEEK",
            frequency_interval=2,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Bi Weekly Call to NOT be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=2, days=0, hours=0, minutes=0),
            frequency_unit="WEEK",
            frequency_interval=2,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Tri Weekly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=2, days=6, hours=23, minutes=30),
            frequency_unit="WEEK",
            frequency_interval=3,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Tri Weekly Call to NOT be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(weeks=3, days=0, hours=0, minutes=0),
            frequency_unit="WEEK",
            frequency_interval=3,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Monthly Call to be NOT executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=31),
            frequency_unit="MONTH",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )

        # Monthly Call to be executed within 30 minutes
        CallSchedule.objects.create(
            receiver=gift_receiver,
            call_title="Morning Standup",
            started_at=now - timedelta(days=30, hours=23, minutes=30),
            frequency_unit="MONTH",
            frequency_interval=1,
            time_zone="US/Eastern",
            is_recurring=True
        )


        # Act
        check_scheduled_call_task.apply()

        # Initialize a counter for expected messages
        expected_message_count = 0
        expected_message = "Recurring call 'Morning Standup' within the next 30 minutes in US/Eastern."
        # Check each call made to mock_print for the expected message
        for mock_call in mock_print.call_args_list:
            # mock_call is a call() object that contains a tuple of (args_list, kwargs)
            # We're interested in args_list, which is the first item in the tuple
            if mock_call[0][0] == expected_message:
                expected_message_count += 1

        # Now expected_message_count contains the number of times your expected message was printed
        print(f"Expected message was printed {expected_message_count} times.")
        self.assertEqual(expected_message_count, 15)
