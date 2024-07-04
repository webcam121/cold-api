from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from agent.apps.accounts.models import CustomUser, GiftGiver, GiftReceiver, Prereceiver
from agent.apps.accounts.permissions import IsGiftGiver, IsGiftReceiver, APIKeyPermission
from agent.apps.questions.models import PersonalQuestion, PersonalQuestionCategory, SystemQuestion, \
    CharacterLimitSetting, Node, Edge
from agent.apps.call_sessions.models import Conversation, TrialConversation, ConversationTopicSummary, ShareLink

from agent.apps.questions.permissions import IsObjectOwner
from agent.apps.questions.serializers import PersonalQuestionSerializer, PersonalQuestionCategorySerializer, \
    CreatePersonalQuestionSerializer, ListPersonalQuestionSerializer, \
    ListSystemQuestionSerializer, ListSystemQuestionForNumberSerializer, \
    UpdatePersonalQuestionSerializer, ListCategoryPersonalQuestionSerializer, \
    CreatePreReceiverPersonalQuestionSerializer, CharacterLimitSettingSerializer, SharedTopicSummarySerializer, \
    LatestPersonalQuestionSerializer, NodeSerializer, EdgeSerializer


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer


class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class CharacterLimitSettingView(APIView):
    permission_classes = [APIKeyPermission]
    serializer_class = CharacterLimitSettingSerializer

    def get(self, request, *args, **kwargs):
        category = request.GET.get('category', 'default')

        character_limit_setting = CharacterLimitSetting.objects.filter(category=category).first()

        if character_limit_setting is not None:
            serializer = self.serializer_class(character_limit_setting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class CharacterLimitSettingView(APIView):
    permission_classes = [APIKeyPermission]
    serializer_class = CharacterLimitSettingSerializer

    def get(self, request, *args, **kwargs):
        category = request.GET.get('category', 'default')

        character_limit_setting = CharacterLimitSetting.objects.filter(category=category).first()

        if character_limit_setting is not None:
            serializer = self.serializer_class(character_limit_setting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class ListQuestionView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = ListSystemQuestionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['receiver_id'] = self.kwargs['gift_receiver_id']
        return context

    # def get(self, request, *args, **kwargs):
    #     gift_giver_user = self.request.user
    #     gift_receiver_id = self.kwargs['gift_receiver_id']  # Getting the gift receiver id from URL
    #
    #     personal_questions = PersonalQuestion.objects.filter(
    #         gift_giver__user=gift_giver_user,
    #         gift_receiver__user__id=gift_receiver_id
    #     )
    #
    #     system_questions = SystemQuestion.objects.all()
    #
    #     personal_serializer = ListPersonalQuestionSerializer(personal_questions, many=True)
    #     # system_serializer = ListSystemQuestionSerializer(system_questions, many=True)
    #     system_serializer = self.get_serializer(system_questions, many=True)
    #
    #     return Response({
    #         'personal_questions': personal_serializer.data,
    #         'system_questions': system_serializer.data
    #     }, status=status.HTTP_200_OK)
    def get_queryset(self):
        gift_giver_user = self.request.user
        gift_receiver_id = self.kwargs['gift_receiver_id']

        # Fetch personal questions with conversations
        personal_questions = PersonalQuestion.objects.filter(
            gift_giver__user=gift_giver_user,
            gift_receiver__user__id=gift_receiver_id,
            personal_conversations__isnull=False  # Filter out questions without conversations
        ).order_by('category__order').distinct()

        # Fetch system questions with conversations
        system_questions = SystemQuestion.objects.filter(
            system_conversations__call_session__receiver__user__id=gift_receiver_id
        ).order_by('category__order').distinct()

        return {
            'personal_questions': personal_questions,
            'system_questions': system_questions
        }

    def list(self, request, *args, **kwargs):
        # Check permission before proceeding
        gift_receiver_id = self.kwargs['gift_receiver_id']
        gift_receiver = get_object_or_404(GiftReceiver, pk=gift_receiver_id)
        gift_giver_user = self.request.user
        if not gift_receiver.gift_giver.filter(user=gift_giver_user).exists():
            return Response({'message': "You don't have permission to perform this action"},
                            status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset()
        personal_serializer = ListPersonalQuestionSerializer(queryset['personal_questions'], many=True)
        system_serializer = self.get_serializer(queryset['system_questions'], many=True)

        data = {
            'personal_questions': personal_serializer.data,
            'system_questions': system_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class ListQuestionForReceiverView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsGiftReceiver]

    serializer_class = ListSystemQuestionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['receiver_id'] = self.request.user.id
        return context

    # def get(self, request, *args, **kwargs):
    #     gift_receiver_user = self.request.user
    #
    #     # Filter PersonalQuestion based on authenticated gift receiver user
    #     personal_questions = PersonalQuestion.objects.filter(gift_receiver__user=gift_receiver_user)
    #     system_questions = SystemQuestion.objects.all()
    #     personal_serializer = ListPersonalQuestionSerializer(personal_questions, many=True)
    #     system_serializer = self.get_serializer(system_questions, many=True)
    #
    #     return Response({
    #         'personal_questions': personal_serializer.data,
    #         'system_questions': system_serializer.data
    #     }, status=status.HTTP_200_OK)
    def get_queryset(self):
        gift_receiver_user = self.request.user

        # Fetch personal questions with conversations
        personal_questions = PersonalQuestion.objects.filter(
            gift_receiver__user=gift_receiver_user,
            personal_conversations__isnull=False  # Filter out questions without conversations
        ).order_by('category__order').distinct()

        # Fetch system questions with conversations
        system_questions = SystemQuestion.objects.filter(
            system_conversations__call_session__receiver__user=gift_receiver_user
        ).order_by('category__order').distinct()

        return {
            'personal_questions': personal_questions,
            'system_questions': system_questions
        }

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        personal_serializer = ListPersonalQuestionSerializer(queryset['personal_questions'], many=True)
        system_serializer = self.get_serializer(queryset['system_questions'], many=True)

        data = {
            'personal_questions': personal_serializer.data,
            'system_questions': system_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class ListQuestionForNumberView(generics.ListAPIView):
    permission_classes = [APIKeyPermission]

    serializer_class = ListSystemQuestionForNumberSerializer

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context['receiver_id'] = self.request.user.id
    #     return context

    def get(self, request, *args, **kwargs):
        phone_number = self.kwargs['phone_number']
        topic_ids = Conversation.objects.filter(
            call_session__phone_number=phone_number,
            system_topic__isnull=False
        ).distinct('system_topic').values_list('system_topic', flat=True)
        # gift_receiver_user = self.request.user
        # gift_giver_user = CustomUser.objects.get(id=self.request.user.id)
        # gift_giver_instance = GiftGiver.objects.get(user=gift_giver_user)
        # gift_receiver_id = self.kwargs['gift_receiver_id']  # Getting the gift receiver id from URL

        # Filter PersonalQuestion based on authenticated gift giver user and gift receiver id
        # personal_questions = PersonalQuestion.objects.filter(gift_receiver__user=gift_receiver_user)
        system_questions = SystemQuestion.objects.exclude(
            id__in=topic_ids
        ).order_by('rank')

        # personal_serializer = ListPersonalQuestionSerializer(personal_questions, many=True)
        # system_serializer = ListSystemQuestionSerializer(system_questions, many=True)
        system_serializer = self.get_serializer(system_questions, many=True)

        return Response({
            # 'personal_questions': personal_serializer.data,
            'system_questions': system_serializer.data
        }, status=status.HTTP_200_OK)


class TrialListQuestionForNumberView(generics.ListAPIView):
    permission_classes = [APIKeyPermission]
    serializer_class = ListSystemQuestionForNumberSerializer

    def get(self, request, *args, **kwargs):
        phone_number = self.kwargs['phone_number']
        topic_ids = TrialConversation.objects.filter(
            call_session__user__phone_number=phone_number,
            system_topic__isnull=False
        ).distinct('system_topic').values_list('system_topic', flat=True)

        system_questions = SystemQuestion.objects.exclude(
            id__in=topic_ids
        ).order_by('rank')

        system_serializer = self.get_serializer(system_questions, many=True)

        return Response({
            'system_questions': system_serializer.data
        }, status=status.HTTP_200_OK)


class DetailPersonalQuestionView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PersonalQuestion.objects.all()
    serializer_class = PersonalQuestionSerializer
    permission_classes = [IsObjectOwner, IsAuthenticated]


class ListPersonalQuestionCategoryView(generics.ListAPIView):
    queryset = PersonalQuestionCategory.objects.all()
    serializer_class = PersonalQuestionCategorySerializer
    permission_classes = [IsAuthenticated]


class CreatePersonalQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = CreatePersonalQuestionSerializer

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        category = get_object_or_404(PersonalQuestionCategory, pk=pk)
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            created_question_ids = []  # List to hold the IDs of created questions
            gift_giver_user = self.request.user
            gift_giver = GiftGiver.objects.get(user=gift_giver_user)

            for question_data in serializer.validated_data:
                question = question_data['question']
                # get GiftReceiver instance
                gift_receiver = get_object_or_404(GiftReceiver, pk=question_data['gift_receiver'])

                if not gift_receiver.gift_giver.filter(user=self.request.user).exists():
                    return Response({"message": "You don't have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
                category = category
                personal_question = PersonalQuestion(question=question, gift_giver=gift_giver, category=category,
                                                     gift_receiver=gift_receiver)
                personal_question.save()
                created_question_ids.append(personal_question.id)  # Append the ID of the created question
            return Response({'created_question_ids': created_question_ids}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatePreReceiverPersonalQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = CreatePreReceiverPersonalQuestionSerializer

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        category = get_object_or_404(PersonalQuestionCategory, pk=pk)
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            created_question_ids = []  # List to hold the IDs of created questions
            gift_giver_user = self.request.user
            gift_giver = GiftGiver.objects.get(user=gift_giver_user)

            for question_data in serializer.validated_data:
                question = question_data['question']
                # get PreReceiver instance
                pre_receiver = get_object_or_404(Prereceiver, pk=question_data['pre_receiver_id'])
                if pre_receiver.giver != gift_giver:
                    return Response({"message": "You don't have permission to do action."}, status=status.HTTP_403_FORBIDDEN)
                category = category
                personal_question = PersonalQuestion(question=question, gift_giver=gift_giver, category=category)
                personal_question.pre_receiver = pre_receiver
                personal_question.save()
                created_question_ids.append(personal_question.id)  # Append the ID of the created question
            return Response({'created_question_ids': created_question_ids}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePersonalQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = UpdatePersonalQuestionSerializer

    def patch(self, request, pk, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True, partial=True)
        if serializer.is_valid():
            gift_giver = get_object_or_404(GiftGiver, user=request.user)
            for question_data in serializer.validated_data:
                question_id = question_data['question_id']
                question_instance = get_object_or_404(PersonalQuestion, pk=question_id)
                if question_instance.gift_giver != gift_giver:
                    return Response({"message": "You don't have permission to do action."}, status=status.HTTP_403_FORBIDDEN)

                # Retrieve the category ID from the validated data
                category = question_data.pop('category', None)
                # Set the category instance if category ID is provided
                if category is not None:
                    question_instance.category = category

                # Create a new serializer instance for each question data
                question_serializer = self.serializer_class(instance=question_instance, data=question_data,
                                                            partial=True)

                if question_serializer.is_valid():
                    question_serializer.save()
                else:
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePrereceiverPersonalQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = UpdatePersonalQuestionSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True, partial=True)

        if serializer.is_valid():
            gift_giver = get_object_or_404(GiftGiver, user=request.user)
            for question_data in serializer.validated_data:
                question_id = question_data['question_id']
                question_instance = get_object_or_404(PersonalQuestion, pk=question_id)
                if question_instance.gift_giver != gift_giver:
                    return Response({"message": "You don't have permission to do action."}, status=status.HTTP_403_FORBIDDEN)
                # Retrieve the category ID from the validated data
                category = question_data.pop('category', None)
                # Set the category instance if category ID is provided
                if category is not None:
                    question_instance.category = category

                # Create a new serializer instance for each question data
                question_serializer = self.serializer_class(instance=question_instance, data=question_data,
                                                            partial=True)

                if question_serializer.is_valid():
                    question_serializer.save()
                else:
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPersonalQuestionView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = ListCategoryPersonalQuestionSerializer

    def get_queryset(self):
        gift_receiver_id = self.kwargs.get('receiver_id')
        gift_receiver = get_object_or_404(GiftReceiver, pk=gift_receiver_id)
        if not gift_receiver.gift_giver.filter(user=self.request.user).exists():
            raise PermissionDenied("You don't have permission to do action")
        category_id = self.kwargs.get('pk')
        category = get_object_or_404(PersonalQuestionCategory, pk=category_id)
        return PersonalQuestion.objects.filter(category=category, gift_receiver__user__id=gift_receiver_id)


class ListPreReceiverPersonalQuestionView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = ListCategoryPersonalQuestionSerializer

    def get_queryset(self):
        pre_receiver_id = self.kwargs.get('receiver_id')
        pre_receiver = get_object_or_404(Prereceiver, pk=pre_receiver_id)
        gift_giver = get_object_or_404(GiftGiver, user=self.request.user)
        if pre_receiver.giver != gift_giver:
            raise PermissionDenied("You don't have permission to do action")
        category_id = self.kwargs.get('pk')
        category = get_object_or_404(PersonalQuestionCategory, pk=category_id)
        pre_receiver_id = self.kwargs.get('receiver_id')
        return PersonalQuestion.objects.filter(category=category, pre_receiver__id=pre_receiver_id)


class SharedStoryView(generics.GenericAPIView):
    serializer_class = SharedTopicSummarySerializer

    def get(self, request, *args, **kwargs):
        share_link = kwargs.get('share_link')
        share_link = get_object_or_404(ShareLink, key=share_link)

        topic_summary = share_link.topic_summary
        user = share_link.user

        receiver = topic_summary.receiver
        receiver_user = receiver.user
        receiver_detail = {
            "first_name": receiver_user.first_name,
            "last_name": receiver_user.last_name,
            "image_url": receiver.user.image.url if receiver.user.image else ""
        }

        user_detail = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        serializer = self.serializer_class(topic_summary)

        return Response({
            'user_detail': user_detail,
            'receiver_detail': receiver_detail,
            'summary': serializer.data
        }, status=status.HTTP_200_OK)


class RetrieveLatestPreReceiverPersonalQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = LatestPersonalQuestionSerializer

    def get(self, request, *args, **kwargs):
        giver_user = self.request.user
        gift_giver = get_object_or_404(GiftGiver, user=giver_user)
        pre_receiver_id = kwargs.get('pre_receiver_id')
        pre_receiver = get_object_or_404(Prereceiver, pk=pre_receiver_id)
        if pre_receiver.giver != gift_giver:
            return Response({"message": "The Giver didn't register this Pre-Receiver"}, status=status.HTTP_403_FORBIDDEN)
        else:
            latest_personal_questions = PersonalQuestion.objects.filter(gift_giver=gift_giver,
                                                                        pre_receiver=pre_receiver)

            if latest_personal_questions:
                serializer = self.serializer_class(latest_personal_questions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No questions found for the gift giver and pre-receiver'},
                                status=status.HTTP_404_NOT_FOUND)


class GenerateShareLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        topic_summary_id = kwargs.get('topic_summary_id')

        topic_summary = get_object_or_404(ConversationTopicSummary, pk=topic_summary_id)

        receiver = topic_summary.receiver
        # Check if user is related to topic summary
        giver = GiftGiver.objects.filter(user=self.request.user).first()
        if receiver.user == user or (giver and giver.gift_receivers.filter(user=receiver.user).exists()):
            share_link = ShareLink(
                key=ShareLink.generate_key(), user=user, topic_summary=topic_summary
            )
            share_link.save()
            return Response({'share_link': share_link.key}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You don't have permission to share this story"}, status=status.HTTP_403_FORBIDDEN)
