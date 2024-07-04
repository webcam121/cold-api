from django.urls import path

from agent.apps.questions.views import DetailPersonalQuestionView, \
    ListPersonalQuestionCategoryView, CreatePersonalQuestionView, \
    ListQuestionView, ListQuestionForReceiverView, ListQuestionForNumberView, UpdatePersonalQuestionView, \
    ListPersonalQuestionView, TrialListQuestionForNumberView, CreatePreReceiverPersonalQuestionView, \
    UpdatePrereceiverPersonalQuestionView, ListPreReceiverPersonalQuestionView, CharacterLimitSettingView, \
    SharedStoryView, RetrieveLatestPreReceiverPersonalQuestionView, GenerateShareLinkView, NodeViewSet, EdgeViewSet

app_name = 'questions'

urlpatterns = [
    path('character-limit-setting/', CharacterLimitSettingView.as_view()),
    path('script/<str:phone_number>/', ListQuestionForNumberView.as_view()),
    path('trial-script/<str:phone_number>/', TrialListQuestionForNumberView.as_view()),
    # path('receivers/', ListQuestionForReceiverView.as_view()),
    # path('receivers/<int:gift_receiver_id>/', ListQuestionView.as_view()),
    path('detail/personal_questions/<int:pk>/', DetailPersonalQuestionView.as_view()),
    path('categories/', ListPersonalQuestionCategoryView.as_view()),
    path('categories/<int:pk>/add_question/', CreatePersonalQuestionView.as_view()),
    path('categories/<int:pk>/update_question/', UpdatePersonalQuestionView.as_view()),
    path('categories/<int:pk>/list_question/<int:receiver_id>/', ListPersonalQuestionView.as_view()),

    # Pre receivers questions
    path('categories/<int:pk>/pre_receiver/add_question/', CreatePreReceiverPersonalQuestionView.as_view()),
    path('categories/<int:pk>/pre_receiver/update_question/', UpdatePrereceiverPersonalQuestionView.as_view()),
    path('categories/<int:pk>/pre_receiver/list_question/<int:receiver_id>/', ListPreReceiverPersonalQuestionView.as_view()),
    path('categories/pre_receiver/<int:pre_receiver_id>/latest/', RetrieveLatestPreReceiverPersonalQuestionView.as_view()),
    path('generate_share_link/<int:topic_summary_id>/', GenerateShareLinkView.as_view()),
    path('shared_stories/<str:share_link>/', SharedStoryView.as_view()),
    path('nodes/', NodeViewSet.as_view({'get': 'list'})),
    path('edges/', EdgeViewSet.as_view({'get': 'list'})),

]
