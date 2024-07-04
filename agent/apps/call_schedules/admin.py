

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from agent.apps.call_schedules.models import CallSchedule


class CallScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'receiver_link',
        'started_at',
        'frequency_unit',
        'frequency_interval',
        'time_zone',
        'is_recurring')
    search_fields = ('call_title',)
    list_filter = ('time_zone', 'is_recurring')
    readonly_fields = ('receiver_link',)
    exclude = ('receiver',)

    def receiver_link(self, obj):
        link = reverse("admin:accounts_giftreceiver_change",
                       args=[obj.receiver.pk])  # app_label and model name might need adjustment
        return format_html('<a href="{}">{}</a>', link, obj.receiver)

    receiver_link.short_description = "Receiver"


admin.site.register(CallSchedule, CallScheduleAdmin)
