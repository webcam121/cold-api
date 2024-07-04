from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings

from agent.apps.accounts.models import ExpiringAuthToken, InvitationToken, CustomUser, GiftGiver, GiftReceiver
from agent.services import expert_sender, zendesk
from agent.services.constants import INVITATION_NOTIFICATION_TO_USER, INVITATION_NOTIFICATION_TO_NONUSER


@shared_task
def add_user_to_expert_sender_blacklist(email):
    expert_sender.add_subscriber_to_blacklist(email)


@shared_task
def send_invitation_email_to_user_from_giver(user_id, giver_id, receiver_id, daily_update):
    user = CustomUser.objects.filter(pk=user_id).first()
    giver = GiftGiver.objects.filter(pk=giver_id).first()
    receiver = GiftReceiver.objects.filter(pk=receiver_id).first()

    token = ExpiringAuthToken(
        key=ExpiringAuthToken.generate_key(), user=user, expire_at=datetime.now() + timedelta(days=7)
    )
    link = f"{settings.FRONTEND_BASE_URL}giver/{receiver.pk}?token={token.key}"
    if zendesk.ZendeskAPI.send_notification(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        subject=f"{giver.user.first_name} {giver.user.last_name} invited you to be their designated contact",
        html_body=generate_invitation_email_to_user_from_giver_content(user, link, giver, receiver, daily_update),
        tags=[INVITATION_NOTIFICATION_TO_USER],
        status='solved',
        sms=False,
    ):
        notification = Notification(notification_type=INVITATION_NOTIFICATION_TO_USER, user=user)
        notification.save()

    token.save()


@shared_task
def send_invitation_email_to_nonuser_from_giver(email, first_name, last_name, phone_number, giver_id, receiver_id, daily_update):
    receiver = GiftReceiver.objects.filter(pk=receiver_id).first()
    giver = GiftGiver.objects.filter(pk=giver_id).first()

    invitation_token = InvitationToken(
        key=InvitationToken.generate_key(),
        user_email=email,
        user_first_name=first_name,
        user_last_name=last_name,
        user_phone_number=phone_number,
        receiver=receiver,
        daily_update=daily_update
    )
    link = f"{settings.FRONTEND_BASE_URL}accept-invitation?invitation_token={invitation_token.key}"

    if zendesk.ZendeskAPI.send_notification(
            first_name="",
            last_name="",
            email=email,
            subject=f"{giver.user.first_name} {giver.user.last_name} invited you to be their designated contact",
            html_body=generate_invitation_email_to_non_user_from_giver_content(link, giver, receiver, daily_update),
            tags=[INVITATION_NOTIFICATION_TO_NONUSER],
            status='solved',
            sms=False,
    ):
        notification = Notification(notification_type=INVITATION_NOTIFICATION_TO_NONUSER, user=receiver.user)
        notification.save()

    invitation_token.save()


@shared_task
def send_invitation_email_to_user_from_receiver(user_id, receiver_id, daily_update):
    user = CustomUser.objects.filter(pk=user_id).first()
    receiver = GiftReceiver.objects.filter(pk=receiver_id).first()
    token = ExpiringAuthToken(
        key=ExpiringAuthToken.generate_key(), user=user, expire_at=datetime.now() + timedelta(days=7)
    )
    link = f"{settings.FRONTEND_BASE_URL}giver/{receiver.pk}?token={token.key}"
    if zendesk.ZendeskAPI.send_notification(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        subject=f"{receiver.user.first_name} {receiver.user.last_name} invited you to be their designated contact",
        html_body=generate_invitation_email_to_user_from_receiver_content(user, link, receiver, daily_update),
        tags=[INVITATION_NOTIFICATION_TO_USER],
        status='solved',
        sms=False,
    ):
        notification = Notification(notification_type=INVITATION_NOTIFICATION_TO_USER, user=user)
        notification.save()

    token.save()


@shared_task
def send_invitation_email_to_nonuser_from_receiver(email, first_name, last_name, phone_number, receiver_id, daily_update):
    receiver = GiftReceiver.objects.filter(pk=receiver_id).first()
    invitation_token = InvitationToken(
        key=InvitationToken.generate_key(),
        user_email=email,
        user_first_name=first_name,
        user_last_name=last_name,
        user_phone_number=phone_number,
        receiver=receiver,
        daily_update=daily_update
    )
    link = f"{settings.FRONTEND_BASE_URL}accept-invitation?invitation_token={invitation_token.key}"

    if zendesk.ZendeskAPI.send_notification(
        first_name="",
        last_name="",
        email=email,
        subject=f"{receiver.user.first_name} {receiver.user.last_name} invited you to be their designated contact",
        html_body=generate_invitation_email_to_non_user_from_receiver_content(link, receiver, daily_update),
        tags=[INVITATION_NOTIFICATION_TO_NONUSER],
        status='solved',
        sms=False,
    ):
        notification = Notification(notification_type=INVITATION_NOTIFICATION_TO_NONUSER, user=receiver.user)
        notification.save()

    invitation_token.save()


