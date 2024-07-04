from rest_framework import serializers

from agent.apps.call_schedules.models import CallSchedule, CallScheduleLog


class CallScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallSchedule
        fields = ['pk', 'created_at', 'updated_at', 'receiver', 'call_title', 'started_at', 'pause_start_date', 'pause_end_date', 'frequency_unit',
                  'frequency_interval', 'time_zone', 'is_recurring', 'description']
        extra_kwargs = {
            'receiver': {'read_only': True},
        }


class CallScheduleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallScheduleLog
        fields = ['pk', 'scheduled_time', 'status', 'call_schedule', 'receiver']


class RescheduleCallSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField(required=True)
    timezone = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
