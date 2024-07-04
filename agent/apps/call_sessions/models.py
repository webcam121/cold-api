import binascii
import os
import uuid

from django.db import models
from django.conf import settings

from agent.apps.accounts.models import GiftReceiver, CustomUser
from agent.apps.questions.models import SystemQuestion, PersonalQuestion
from agent.storage_backends import PrivateMediaStorage


def callsession_audio_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/callsession-audio/{instance.pk}/{filename}'


def trial_callsession_audio_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/trialcallsession-audio/{instance.pk}/{filename}'


def conversation_audio_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/conversation-audio/{instance.pk}/{filename}'


def trial_conversation_audio_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/trialconversation-audio/{instance.pk}/{filename}'


def conversation_summary_audio_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/conversation-summary-audio/{instance.pk}/{filename}'


def digital_persona_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/digital-persona/{instance.pk}/{filename}'


def biography_file_upload_to_path(instance, filename):
    return f'{settings.ENVIRONMENT}/biography/{instance.pk}/{filename}'


class CallSession(models.Model):
    DIRECTION_TYPE = [
        ('Inbound', 'Inbound'),
        ('Outbound', 'Outbound'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    phone_number = models.CharField(max_length=250, null=True, blank=True)
    audio = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                             upload_to=callsession_audio_file_upload_to_path)
    summary = models.TextField(null=True, blank=True)
    analyzer_summary = models.TextField(null=True, blank=True)
    system_prompt = models.TextField(null=True, blank=True)
    direction = models.CharField(choices=DIRECTION_TYPE, max_length=120, null=False, blank=False)

    class Meta:
        verbose_name = 'Call Session'
        verbose_name_plural = 'Call Sessions'

    def __str__(self):
        return str(self.pk)


class TrialCallSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='trial_call_session', null=True, blank=True)
    phone_number = models.CharField(max_length=250, null=True, blank=True)
    audio = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                             upload_to=trial_callsession_audio_file_upload_to_path)


    class Meta:
        verbose_name = 'Trial Call Session'
        verbose_name_plural = 'Trial Call Sessions'

    def __str__(self):
        return str(self.pk)

class Conversation(models.Model):
    ROLE_TYPE = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    call_session = models.ForeignKey(CallSession, on_delete=models.CASCADE, related_name='conversation',
                                     null=False, blank=False)
    role = models.CharField(choices=ROLE_TYPE, max_length=10, null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    system_topic = models.ForeignKey(SystemQuestion, on_delete=models.CASCADE, related_name='system_conversations',
                                     blank=True, null=True)
    personal_topic = models.ForeignKey(PersonalQuestion, on_delete=models.CASCADE,
                                       related_name='personal_conversations', null=True, blank=True)
    postfix = models.TextField(blank=True, null=True)
    save_time = models.DateTimeField(blank=True, null=True)
    audio = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                             upload_to=conversation_audio_file_upload_to_path)

    def __str__(self):
        return str(self.pk)


class SystemPrompt(models.Model):
    CATEGORY_TYPE = [
        ('introduction', 'Introduction'),
        ('default', 'Default'),
        ('trial', 'Trial'),
        ('notrivia', 'No Trivia'),
    ]
    DIRECTION_TYPE = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(null=False, blank=False)
    category = models.CharField(choices=CATEGORY_TYPE, max_length=120, null=False, blank=False)
    direction = models.CharField(choices=DIRECTION_TYPE, max_length=120, null=False, blank=False)

    def save(self, *args, **kwargs):
        if self.content:
            # Normalize line endings to Unix-style
            self.content = self.content.replace('\r\n', '\n')

        super(SystemPrompt, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.category} - {self.direction}'

    class Meta:
        verbose_name = 'System Prompt'
        verbose_name_plural = 'System Prompts'


class PostfixPrompt(models.Model):
    PROMPT_TYPE = [
        ('first_topic', 'First Topic'),
        ('next_topic', 'Next Topic'),
        ('end_topic', 'End Topic'),
        ('postfix_template', 'Postfix Template'),
    ]
    CATEGORY_TYPE = [
        ('default', 'Default'),
        ('trial', 'Trial'),
        ('notrivia', 'No Trivia')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(null=False, blank=False)
    prompt_type = models.CharField(choices=PROMPT_TYPE, max_length=120, null=False, blank=False)
    category = models.CharField(choices=CATEGORY_TYPE, max_length=120, default='default', null=False, blank=False)

    def save(self, *args, **kwargs):
        if self.content:
            # Normalize line endings to Unix-style
            self.content = self.content.replace('\r\n', '\n')
            self.content = self.content.replace('\\n', '\n')

        super(PostfixPrompt, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.prompt_type}'

    class Meta:
        verbose_name = 'Postfix Prompt'
        verbose_name_plural = 'Postfix Prompts'


class SummarySettings(models.Model):
    SUMMARY_TYPE = [
        ('session_summary', 'Session Summary'),
        ('conversation_summary', 'Conversation Summary'),
        ('analyze_session_summary', 'Analyze Session Summary'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model = models.CharField(max_length=255, null=False, blank=False)
    temperature = models.FloatField(null=False, blank=False)
    max_tokens = models.IntegerField(null=False, blank=False, default=250)
    prompt = models.TextField(null=False, blank=False)
    summary_type = models.CharField(choices=SUMMARY_TYPE, max_length=120, null=False, blank=False)

    class Meta:
        verbose_name = 'Summary Settings'
        verbose_name_plural = 'Summary Settings'

    def __str__(self):
        return f'{self.model} - {self.temperature} - {self.max_tokens}'


class ConversationTopicSummary(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    summary = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    receiver = models.ForeignKey(GiftReceiver, on_delete=models.CASCADE, related_name='topic_summaries',
                                 null=False, blank=False)
    audio = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                             upload_to=conversation_summary_audio_file_upload_to_path)
    system_topic = models.ForeignKey(SystemQuestion, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='system_topic_summaries')
    personal_topic = models.ForeignKey(PersonalQuestion, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='personal_topic_summaries')
    share_link = models.CharField(max_length=55, null=True, blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.share_link:
            self.share_link = uuid.uuid4().hex
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Conversation Topic Summary'
        verbose_name_plural = 'Conversation Topic Summaries'

    def __str__(self):
        return str(self.pk)


class DigitalPersona(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    digital_persona = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                                       upload_to=digital_persona_file_upload_to_path)
    receiver = models.OneToOneField(GiftReceiver, on_delete=models.CASCADE, related_name='digital_persona', null=True,
                                    blank=True)

    class Meta:
        verbose_name = 'Digital Persona'
        verbose_name_plural = 'Digital Personas'

    def __str__(self):
        return str(self.pk)


class Biography(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    biography = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                                 upload_to=biography_file_upload_to_path)
    receiver = models.OneToOneField(GiftReceiver, on_delete=models.CASCADE, related_name='biography', null=True,
                                    blank=True)

    class Meta:
        verbose_name = 'Biography'
        verbose_name_plural = 'Biographies'

    def __str__(self):
        return str(self.pk)


class TrialConversation(models.Model):
    ROLE_TYPE = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    call_session = models.ForeignKey(TrialCallSession, on_delete=models.CASCADE, related_name='conversation',
                                     null=False, blank=False)
    role = models.CharField(choices=ROLE_TYPE, max_length=10, null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    system_topic = models.ForeignKey(SystemQuestion, on_delete=models.CASCADE, related_name='trial_system_conversations',
                                     blank=True, null=True)
    postfix = models.TextField(blank=True, null=True)
    save_time = models.DateTimeField(blank=True, null=True)
    audio = models.FileField(null=True, blank=True, storage=PrivateMediaStorage(),
                             upload_to=trial_conversation_audio_file_upload_to_path)

    def __str__(self):
        return str(self.pk)


class ShareLink(models.Model):
    key = models.CharField(max_length=40, primary_key=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, related_name='shared_links')
    topic_summary = models.ForeignKey(ConversationTopicSummary, on_delete=models.CASCADE, null=False,
                                      related_name='topic_shared_links')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Shared Link"
        verbose_name_plural = "Shared Links"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return str(self.pk)