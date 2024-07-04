from django.db import models
import pytz

from agent.apps.accounts.models import GiftReceiver


class CallSchedule(models.Model):
    FREQ_UNIT = [('DAY', 'Day'), ('WEEK', 'Week'), ('MONTH', 'Month')]
    TIMEZONES = [
        ('US/Eastern', 'US/Eastern'),
        ('US/Central', 'US/Central'),
        ('US/Mountain', 'US/Mountain'),
        ('US/Pacific', 'US/Pacific')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    receiver = models.ForeignKey(GiftReceiver, on_delete=models.CASCADE, related_name='call_schedule', blank=False, null=False)
    # scheduled time fields
    call_title = models.CharField(max_length=255, null=True, blank=True)
    started_at = models.DateTimeField(null=False, blank=False)
    pause_start_date = models.DateField(null=True, blank=True)
    pause_end_date = models.DateField(null=True, blank=True)
    frequency_unit = models.CharField(choices=FREQ_UNIT, max_length=55, null=False, blank=False,
                                      help_text="Frequency unit for scheduling")
    frequency_interval = models.IntegerField(default=1, null=False, blank=False,
                                             help_text="Interval for scheduling frequency")
    time_zone = models.CharField(max_length=50, choices=TIMEZONES, default='US/Eastern',
                                 help_text="Timezone to use for scheduling")
    is_recurring = models.BooleanField(default=True, blank=False, null=False,
                                       help_text="Is this a recurring schedule?")
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Call Schedule'
        verbose_name_plural = 'Call Schedules'

    def __str__(self):
        return str(self.pk)


class CallScheduleLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_time = models.DateTimeField(null=False, blank=False)
    status = models.CharField(max_length=55, null=False, blank=False)
    call_schedule = models.ForeignKey(CallSchedule, on_delete=models.CASCADE, related_name='call_schedule_log', blank=False, null=False)
    receiver = models.ForeignKey(GiftReceiver, on_delete=models.CASCADE, related_name='call_schedule_log', blank=False, null=False)

    class Meta:
        verbose_name = 'Call Schedule Log'
        verbose_name_plural = 'Call Schedule Logs'

    def __str__(self):
        return f'{self.scheduled_time} {self.status}'
