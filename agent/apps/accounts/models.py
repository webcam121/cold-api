import binascii
import os
from datetime import datetime, timedelta

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from safedelete.models import SOFT_DELETE, SafeDeleteModel
from django.utils.translation import ugettext_lazy as _

from agent.apps.accounts.managers import CustomUserManager
from agent.storage_backends import PrivateMediaStorage


def dating_bio_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/bio-img/{instance.pk}/{filename}'


class CustomUser(DirtyFieldsMixin, SafeDeleteModel, AbstractUser):
    GENDER_TYPE = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    _safedelete_policy = SOFT_DELETE
    username = None
    email = models.EmailField(_('email address'), unique=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=False, null=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=False, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_TYPE, max_length=10, null=True, blank=True)
    unsubscribed = models.BooleanField(default=False)
    image = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                             upload_to=dating_bio_file_upload_to_path)
    referral_link = models.CharField(max_length=255, blank=True, null=True)
    origin_domain = models.CharField(max_length=255, blank=True, null=True)
    password_updated_at = models.DateTimeField(blank=True, null=True)
    is_giver = models.BooleanField(default=True)
    is_receiver = models.BooleanField(default=False)
    trivia = models.BooleanField(default=True)
    self_gift = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        # Remove dashes from the phone number
        if self.phone_number:
            self.phone_number = self.phone_number.replace("-", "")
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def delete(self, force_policy=None, *args, **kwargs):
        self.email = None
        self.first_name = None
        self.last_name = None
        self.phone_number = None

        if self.is_giver:
            self.giftgiver.delete()

        if self.is_receiver:
            self.giftreceiver.delete()

        self.is_giver = False
        self.is_receiver = False

        super().delete(*args, **kwargs)


class GiftGiver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.user.email)

    class Meta:
        verbose_name = 'Gift Giver'
        verbose_name_plural = 'Gift Givers'


class ExpiringAuthToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, related_name='expiring_auth_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("ExpiringAuthToken")
        verbose_name_plural = _("ExpiringAuthTokens")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = self.generate_key()
        if not self.expire_at:
            self.expire_at = datetime.now() + timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS)
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(4)).decode()

    def __str__(self):
        return str(self.pk)


class GiftReceiver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    gift_giver = models.ManyToManyField(GiftGiver, related_name='gift_receivers')

    def __str__(self):
        return str(self.user.email)

    class Meta:
        verbose_name = 'Gift Receiver'
        verbose_name_plural = 'Gift Receivers'


class ClientAPIKey(models.Model):
    client_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Client API Key'
        verbose_name_plural = 'Client API Keys'


class Prereceiver(models.Model):
    GENDER_TYPE = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    first_name = models.CharField(_('first name'), max_length=150, blank=False, null=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=False, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_TYPE, max_length=10, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=False, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=False)
    giver = models.ForeignKey(GiftGiver, on_delete=models.CASCADE, related_name='pre_receivers', null=True, blank=True)
    receiver = models.OneToOneField(GiftReceiver, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = 'Pre Receiver'
        verbose_name_plural = 'Pre Receivers'

    def save(self, *args, **kwargs):
        # Remove dashes from the phone number
        if self.phone_number:
            self.phone_number = self.phone_number.replace("-", "")
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class InvitationToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True, blank=True)
    user_email = models.EmailField(unique=False, null=False, blank=False)
    user_first_name = models.CharField(_('first name'), max_length=150, blank=True, null=True)
    user_last_name = models.CharField(_('last name'), max_length=150, blank=True, null=True)
    user_phone_number = models.CharField(_('phone number'), max_length=15, blank=True, null=True)
    receiver = models.ForeignKey(GiftReceiver, on_delete=models.CASCADE, null=False, blank=False,
                                 related_name='receiver_invitation_tokens')
    daily_update = models.BooleanField(null=True, blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Invitation Token")
        verbose_name_plural = _("Invitation Tokens")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = self.generate_key()
        if not self.expire_at:
            self.expire_at = datetime.now() + timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS)
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return str(self.pk)


class DailyUpdate(models.Model):
    gift_giver = models.ForeignKey(GiftGiver, on_delete=models.CASCADE, related_name='giver_daily_updates')
    gift_receiver = models.ForeignKey(GiftReceiver, on_delete=models.CASCADE, related_name='receiver_daily_updates')
    is_daily_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)
