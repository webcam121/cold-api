from django.urls import path
from .views import ListCallSessionView, DetailCallSessionView, StartCallSessionAPIView, EndCallSessionAPIView, \
    ConversationWebhookAPIView, SystemPromptListView, PostfixPromptListView, PhoneCallSystemPromptView, \
    BiographyDetailView, TrialStartCallSessionAPIView, TrialEndCallSessionAPIView, TrialConversationWebhookAPIView, \
    TrialListCallSessionView, ListCallSessionForReceiverView, ListCallSessionForGiverView, OutboundCallView

app_name = 'call_sessions'

urlpatterns = [
    path('outbound-call/', OutboundCallView.as_view(), name='index'),
    path('phone_number/<str:phone_number>/', ListCallSessionView.as_view()),
    path('trial_phone_number/<str:phone_number>/', TrialListCallSessionView.as_view()),
    path('detail/<int:pk>/', DetailCallSessionView.as_view()),
    path('start-call/', StartCallSessionAPIView.as_view()),
    path('trial-start-call/', TrialStartCallSessionAPIView.as_view()),
    path('end-call/<int:pk>/', EndCallSessionAPIView.as_view()),
    path('trial-end-call/<int:pk>/', TrialEndCallSessionAPIView.as_view()),
    path('conversation/<int:pk>/', ConversationWebhookAPIView.as_view()),
    path('trial-conversation/<int:pk>/', TrialConversationWebhookAPIView.as_view()),
    path('system-prompts/', SystemPromptListView.as_view(), name='system-prompts-list'),
    path('system-prompts/<str:phone_number>/', PhoneCallSystemPromptView.as_view(), name='system-prompts'),
    path('postfix-prompts/', PostfixPromptListView.as_view(), name='postfix-prompts-list'),
    # path('digital-persona/<int:receiver_id>/', DigitalPersonaDetailView.as_view()),
    path('biography/<int:receiver_id>/', BiographyDetailView.as_view()),

    path('receivers/', ListCallSessionForReceiverView.as_view()),
    path('receivers/<int:gift_receiver_id>/', ListCallSessionForGiverView.as_view()),
]
