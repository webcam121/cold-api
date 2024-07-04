from django.urls import include, path

from agent.apps.accounts.views import UpdateProfileView, DetailCallerPhoneNumberView

app_name = 'apis'

urlpatterns = [
    path('gift_receivers/', include('agent.apps.accounts.urls', namespace='gift_receivers')),
    path('questions/', include('agent.apps.questions.urls', namespace='questions')),
    path('call_sessions/', include('agent.apps.call_sessions.urls', namespace='call_sessions')),
    path('call_schedules/', include('agent.apps.call_schedules.urls', namespace='call_schedules')),
    path('users/profile/update/', UpdateProfileView.as_view()),
    path('users/phone_number/<str:phone_number>/', DetailCallerPhoneNumberView.as_view()),
]
