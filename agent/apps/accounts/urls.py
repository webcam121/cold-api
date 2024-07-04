from django.urls import path

from agent.apps.accounts.views import ListGiftReceiverView, DetailGiftReceiverView, \
    TrialDetailGiftReceiverByPhoneNumberView, \
    RegisterPreGiftReceiverView, DetailPreGiftReceiverView, UpdatePreReceiver, RetrieveMostRecentPreReceiver, \
    DetailPreReceiverByGiverPhoneNumberView, DetailPaidGiverByReceiverPhoneNumberView, \
    ListPreReceiverView, SkipTriviaGameView

app_name = 'gift_receivers'

urlpatterns = [
    path('', ListGiftReceiverView.as_view()),
    path('trial_phone_number/<str:phone_number>/', TrialDetailGiftReceiverByPhoneNumberView.as_view()),
    path('phone_number/<str:phone_number>/pre_receiver/', DetailPreReceiverByGiverPhoneNumberView.as_view()),
    path('phone_number/<str:phone_number>/paid_giver/', DetailPaidGiverByReceiverPhoneNumberView.as_view()),
    path('trivia_game/reset/<str:phone_number>/', SkipTriviaGameView.as_view()),
    path('receivers/<int:pk>/', DetailGiftReceiverView.as_view()),
    # for pre receivers
    path('pre_receivers/', ListPreReceiverView.as_view()),
    path('pre_receivers/register/', RegisterPreGiftReceiverView.as_view()),
    path('pre_receivers/latest/', RetrieveMostRecentPreReceiver.as_view()),
    path('pre_receivers/<int:pk>/', DetailPreGiftReceiverView.as_view()),
    path('pre_receivers/<int:pk>/update/', UpdatePreReceiver.as_view()),
]
