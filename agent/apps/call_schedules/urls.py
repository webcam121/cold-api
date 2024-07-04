from django.urls import path

from agent.apps.call_schedules.views import DetailCallScheduleView, ListCallScheduleView, CreateCallScheduleView, \
    RescheduleCallView, ListCallScheduleForGiverView, CallScheduleLogView, ListCallScheduleLogView

app_name = 'call_schedules'

urlpatterns = [
    # path('receiver/<int:receiver_id>/', ListCallScheduleForGiverView.as_view()),
    path('receiver/', ListCallScheduleView.as_view()),
    path('', CreateCallScheduleView.as_view()),
    path('detail/<int:pk>/', DetailCallScheduleView.as_view()),
    path('create/reschedule/', RescheduleCallView.as_view()),
    path('call_schedule_log/status/update/', CallScheduleLogView.as_view(), name='call_schedule_log'),
    path('call_schedule_log/<str:phone_number>/', ListCallScheduleLogView.as_view(), name='call_schedule_log'),
]
