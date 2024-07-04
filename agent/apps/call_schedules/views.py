import json
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from agent.apps.accounts.models import CustomUser, GiftReceiver
from agent.apps.call_sessions.models import CallSession
from agent.apps.accounts.permissions import IsGiftReceiver, IsGiftGiver, APIKeyPermission
from agent.apps.call_schedules.models import CallSchedule, CallScheduleLog
from agent.apps.call_schedules.permissions import IsObjectOwner
from agent.apps.call_schedules.serializers import CallScheduleSerializer, RescheduleCallSerializer, CallScheduleLogSerializer


class ListCallScheduleForGiverView(generics.ListAPIView):
    serializer_class = CallScheduleSerializer
    permission_classes = [IsAuthenticated, IsGiftGiver]

    def get_queryset(self):
        receiver_id = self.kwargs['receiver_id']
        receiver = get_object_or_404(GiftReceiver, pk=receiver_id)
        if not receiver.gift_giver.filter(user=self.request.user).exists():
            raise PermissionDenied("You don't have permission to do this action")
        return CallSchedule.objects.filter(receiver__pk=receiver_id)


class ListCallScheduleView(generics.ListAPIView):
    serializer_class = CallScheduleSerializer
    permission_classes = [IsAuthenticated, IsGiftReceiver]

    def get_queryset(self):
        receiver_id = self.request.user.id
        # Order by 'created_at' in descending order to get the latest created object first
        return CallSchedule.objects.filter(receiver__pk=receiver_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().first()  # Get the latest object
        if queryset:
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        else:
            return Response([])  # Return an empty response or however you wish to handle no results


class CreateCallScheduleView(generics.CreateAPIView):
    serializer_class = CallScheduleSerializer
    permission_classes = [IsAuthenticated, IsGiftReceiver]

    def perform_create(self, serializer):
        gift_receiver_user = CustomUser.objects.get(id=self.request.user.id)
        gift_receiver = GiftReceiver.objects.get(user=gift_receiver_user)
        serializer.save(receiver=gift_receiver)


class RescheduleCallView(APIView):
    serializer_class = RescheduleCallSerializer
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            receiver = GiftReceiver.objects.filter(user__phone_number=serializer.validated_data['phone_number']).first()
            if receiver:
                CallSchedule.objects.create(
                    receiver=receiver,
                    started_at=serializer.validated_data['datetime'],
                    time_zone=serializer.validated_data['timezone'],
                    frequency_unit='DAY',
                    is_recurring=False
                )
                return Response({'success': True}, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListCallScheduleLogView(APIView):
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        phone_number = self.kwargs['phone_number']
        receiver = GiftReceiver.objects.filter(user__phone_number=phone_number).first()
        if receiver:
            today = timezone.now().date()
            schedule_logs = CallScheduleLog.objects.filter(
             receiver=receiver,
             scheduled_time__date=today,
            )

            serializer = CallScheduleLogSerializer(schedule_logs, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CallScheduleLogView(APIView):
    permission_classes = [APIKeyPermission]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        call_status = request.data.get('status')

        receiver = GiftReceiver.objects.filter(user__phone_number=phone_number).first()
        if receiver:
            call_schedule = CallSchedule.objects.filter(receiver=receiver).first()
            timestamp = timezone.now() - timedelta(minutes=120)

            schedule_logs = CallScheduleLog.objects.filter(
                receiver=receiver,
                scheduled_time__gte=timestamp,
            ).order_by('-scheduled_time')

            if schedule_logs:
                schedule_log = schedule_logs.first()
                schedule_log.status = call_status
                schedule_log.save()
                if call_status == 'no-answer':
                    call_session = CallSession.objects.filter(
                        receiver=receiver,
                        start_time__gte=timestamp,
                    ).first()
                    if not call_session:
                        if schedule_logs.count() > 3:
                            # send warning notification when we tried to reach the receiver 3 times, but he didn't
                            # answer the call

                            return Response({'success': True}, status=status.HTTP_200_OK)
                        elif schedule_logs.count() == 1:
                            # tasks.run_scheduled_call.apply_async((schedule_log.call_schedule.id,), countdown=600)
                            run_at_time = schedule_logs.last().scheduled_time + timedelta(minutes=10)

                        elif schedule_logs.count() == 2:
                            # tasks.run_scheduled_call.apply_async((schedule_log.call_schedule.id,), countdown=1800)
                            run_at_time = schedule_logs.last().scheduled_time + timedelta(minutes=30)

                        else:
                            # tasks.run_scheduled_call.apply_async((schedule_log.call_schedule.id,), countdown=3600)
                            run_at_time = schedule_logs.last().scheduled_time + timedelta(minutes=60)

            return Response({'success': True}, status=status.HTTP_201_CREATED)


class DetailCallScheduleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CallSchedule.objects.all()
    serializer_class = CallScheduleSerializer
    permission_classes = [IsAuthenticated, IsGiftReceiver, IsObjectOwner]
