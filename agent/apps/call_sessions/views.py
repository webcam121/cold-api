import json
import pdb
from datetime import timedelta, datetime
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
from rest_framework.renderers import TemplateHTMLRenderer
import io
import re
from pydub import AudioSegment


from .models import CallSession, GiftReceiver, SystemPrompt, PostfixPrompt, DigitalPersona, Biography, TrialCallSession
from .permissions import IsObjectOwner
from .serializers import CallSessionSerializer, StartCallSessionSerializer, \
    ConversationSerializer, SystemPromptSerializer, PostfixPromptSerializer, DigitalPersonaSerializer, \
    BiographySerializer, TrialConversationSerializer, TrialStartCallSessionSerializer, TrialCallSessionSerializer

from agent.apps.accounts.models import CustomUser
from ..accounts.permissions import APIKeyPermission, IsGiftGiver, IsGiftReceiver


class OutboundCallView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'apps/call_sessions/index.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        response = requests.post(f'{settings.AGENT_CALL_API_URL}/outgoing/',
                                 json={
                                        'from_number': settings.TWILIO_PHONE_NUMBER,
                                        'to_number': data.get('to_number'),
                                        'transfer_to': data.get('transfer_to'),
                                 })
        return Response({'success': True}, status=status.HTTP_201_CREATED)


class ListCallSessionView(generics.ListAPIView):
    queryset = CallSession.objects.all()
    serializer_class = CallSessionSerializer
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        phone_number = self.kwargs.get('phone_number')

        queryset = self.queryset.filter(phone_number=phone_number)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ListCallSessionForReceiverView(generics.ListAPIView):
    queryset = CallSession.objects.all()
    serializer_class = CallSessionSerializer
    permission_classes = [IsAuthenticated, IsGiftReceiver]

    def get(self, request, *args, **kwargs):
        receiver = GiftReceiver.objects.filter(user=request.user).first()

        # Get start date and end date query parameters from the request
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        # Parse the date strings into date objects
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        queryset = self.queryset.filter(receiver=receiver, summary__isnull=False).order_by('-created_at')

        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date + timedelta(days=1))

        # Limit the queryset to the latest 100 entries
        queryset = queryset[:100]

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListCallSessionForGiverView(generics.ListAPIView):
    queryset = CallSession.objects.all()
    serializer_class = CallSessionSerializer
    permission_classes = [IsAuthenticated, IsGiftGiver]

    def get(self, request, *args, **kwargs):
        # Check permission before proceeding
        gift_receiver_id = self.kwargs['gift_receiver_id']
        gift_receiver = get_object_or_404(GiftReceiver, pk=gift_receiver_id)
        gift_giver_user = self.request.user
        if not gift_receiver.gift_giver.filter(user=gift_giver_user).exists():
            return Response({'message': "You don't have permission to perform this action"},
                            status=status.HTTP_403_FORBIDDEN)

        # Get start date and end date query parameters from the request
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        # Parse the date strings into date objects
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        queryset = self.queryset.filter(receiver=gift_receiver, summary__isnull=False).order_by('-created_at')

        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date + timedelta(days=1))

        # Limit the queryset to the latest 100 entries
        queryset = queryset[:100]
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrialListCallSessionView(generics.ListAPIView):
    queryset = TrialCallSession.objects.all()
    serializer_class = TrialCallSessionSerializer
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        phone_number = self.kwargs.get('phone_number')
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if user:
            queryset = self.queryset.filter(user=user)
        else:
            queryset = self.queryset.filter(phone_number=phone_number)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailCallSessionView(generics.RetrieveAPIView):
    queryset = CallSession.objects.all()
    serializer_class = CallSessionSerializer
    permission_classes = [IsAuthenticated, IsObjectOwner]


class StartCallSessionAPIView(APIView):
    serializer_class = StartCallSessionSerializer
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid():
                pn = serializer.validated_data['phone_number']
                # if user:
                direction = serializer.validated_data['direction']
                system_prompt = serializer.validated_data['system_prompt']
                start_time = timezone.now()
                call_session = CallSession(phone_number=pn, direction=direction, start_time=start_time, system_prompt=system_prompt)
                call_session.save()
                return Response({'call_session_id': call_session.pk}, status=status.HTTP_201_CREATED)
                # return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TrialStartCallSessionAPIView(APIView):
    serializer_class = TrialStartCallSessionSerializer
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.filter(phone_number=serializer.validated_data['phone_number']).first()
            if user:
                call_session = TrialCallSession(user=user, start_time=timezone.now())
                call_session.save()
            else:
                call_session = TrialCallSession(phone_number=serializer.validated_data['phone_number'], start_time=timezone.now())
                call_session.save()
            return Response({'call_session_id': call_session.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EndCallSessionAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        call_session = get_object_or_404(CallSession, pk=pk)
        call_session.end_time = timezone.now()
        call_session.save()

        return Response({'message': 'Call session ended successfully'}, status=status.HTTP_200_OK)


class TrialEndCallSessionAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        call_session = get_object_or_404(TrialCallSession, pk=pk)

        call_session.end_time = timezone.now()
        call_session.save()
        return Response({'message': 'Call session ended successfully'}, status=status.HTTP_200_OK)


class ConversationWebhookAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ConversationSerializer
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        audio_file = request.FILES.get('audio')
        call_session = get_object_or_404(CallSession, pk=pk)
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid():
                conversation = serializer.save(call_session=call_session)
                if audio_file:
                    # Process the audio file (assuming it's in raw format suitable for processing)
                    audio = AudioSegment.from_file(audio_file, format="raw", frame_rate=8000, channels=1, sample_width=2)
                    processed_audio_file_io = io.BytesIO()
                    audio.export(processed_audio_file_io, format="wav")

                    # Save processed audio to the conversation
                    conversation.audio.save("audio.wav", ContentFile(processed_audio_file_io.getvalue()))
                    conversation.save()
                return Response({'success': True}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'SERVER_ERROR': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrialConversationWebhookAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TrialConversationSerializer
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        audio_file = request.FILES.get('audio')
        call_session = get_object_or_404(TrialCallSession, pk=pk)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save(call_session=call_session)
            if audio_file:
                # Process the audio file (assuming it's in raw format suitable for processing)
                audio = AudioSegment.from_file(audio_file, format="raw", frame_rate=8000, channels=1, sample_width=2)
                processed_audio_file_io = io.BytesIO()
                audio.export(processed_audio_file_io, format="wav")

                # Save processed audio to the conversation
                conversation.audio.save("audio.wav", ContentFile(processed_audio_file_io.getvalue()))
                conversation.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SystemPromptListView(generics.ListAPIView):
    serializer_class = SystemPromptSerializer
    queryset = SystemPrompt.objects.all()
    permission_classes = [APIKeyPermission]

    def get_queryset(self):
        category = self.request.query_params.get('category')
        direction = self.request.query_params.get('direction')
        queryset = self.queryset
        if category is not None:
            queryset = queryset.filter(category=category)
        if direction is not None:
            queryset = queryset.filter(direction=direction)
        return queryset


class PhoneCallSystemPromptView(APIView):
    serializer_class = SystemPromptSerializer
    queryset = SystemPrompt.objects.all()
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        try:
            category = self.kwargs.get('category')
            direction = self.kwargs.get('direction')
            queryset = self.get_queryset()
            if category is not None:
                queryset = queryset.filter(category=category)
            if direction is not None:
                queryset = queryset.filter(direction=direction)

            system_prompt = queryset.first()
            content = system_prompt.content.format(
                health="",
                activities="",
                receiver_first_name="",
            )

            return Response({
                'results': [
                    {
                        'content': content
                    }
                ]
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        category = self.request.query_params.get('category')
        direction = self.request.query_params.get('direction')
        queryset = self.queryset
        if category is not None:
            queryset = queryset.filter(category=category)
        if direction is not None:
            queryset = queryset.filter(direction=direction)
        return queryset


class PostfixPromptListView(generics.ListAPIView):
    queryset = PostfixPrompt.objects.all()
    serializer_class = PostfixPromptSerializer
    permission_classes = [APIKeyPermission]

    def get_queryset(self):
        queryset = PostfixPrompt.objects.all()
        category = self.request.query_params.get('category', 'default')
        return queryset.filter(category=category)


class DigitalPersonaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = DigitalPersonaSerializer

    def get(self, request, *args, **kwargs):
        giver_user = self.request.user
        receiver_id = self.kwargs.get('receiver_id')

        # Check if UserPlan exists for giver and receiver pair
        user_plan_exists = UserPlan.objects.filter(giver__user=giver_user, receiver__user__id=receiver_id,
                                                   is_active=True).exists()
        if user_plan_exists:
            digital_persona = get_object_or_404(DigitalPersona, receiver__user__id=receiver_id)
            serializer = DigitalPersonaSerializer(digital_persona)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Subscription for giver and receiver pair has not been active.'}, status=400)


class BiographyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = BiographySerializer

    def get(self, request, *args, **kwargs):
        giver_user = self.request.user
        receiver_id = self.kwargs.get('receiver_id')

        # Check if UserPlan exists for giver and receiver pair
        user_plan_exists = UserPlan.objects.filter(giver__user=giver_user, receiver__user__id=receiver_id,
                                                   is_active=True).exists()
        if user_plan_exists:
            biography = get_object_or_404(Biography, receiver__user__id=receiver_id)
            serializer = DigitalPersonaSerializer(biography)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Subscription for giver and receiver pair has not been active.'}, status=400)
