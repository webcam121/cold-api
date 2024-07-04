from django.contrib import admin
from agent.apps.call_sessions.models import CallSession, Conversation, SystemPrompt, PostfixPrompt, SummarySettings, \
    ConversationTopicSummary, DigitalPersona, Biography, TrialConversation, TrialCallSession, ShareLink


class TrialConversationInline(admin.TabularInline):
    model = TrialConversation
    fields = ('content', 'role', 'call_session', 'system_topic', 'postfix',
              'save_time', 'created_at')
    readonly_fields = ('call_session', 'role', 'content', 'created_at', 'updated_at', 'system_topic', 'audio', 'save_time', 'postfix')
    extra = 0
    ordering = ('save_time',)


@admin.register(TrialCallSession)
class TrialCallSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'audio', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'user', 'start_time', 'end_time', 'audio')
    inlines = [
        TrialConversationInline
    ]


@admin.register(TrialConversation)
class TrialConversationAdmin(admin.ModelAdmin):
    list_display = ('call_session', 'role', 'content', 'system_topic', 'audio', 'save_time', 'created_at', 'updated_at')
    readonly_fields = ('call_session', 'role', 'content', 'created_at', 'updated_at', 'system_topic', 'audio', 'save_time')
    ordering = ('-save_time',)


@admin.register(SummarySettings)
class CallSessionSummarySettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'summary_type', 'model', 'temperature', 'max_tokens', 'created_at', 'updated_at', )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PostfixPrompt)
class PostfixPromptAdmin(admin.ModelAdmin):
    list_display = ('prompt_type', 'category', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('prompt_type',)


@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'direction', 'category')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ConversationTopicSummary)
class ConversationTopicSummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'summary', 'system_topic', 'personal_topic', 'share_link', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'system_topic', 'personal_topic', 'receiver')


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'topic_summary', 'created_at')
    readonly_fields = ('created_at', 'user', 'topic_summary')


class ConversationInline(admin.TabularInline):
    model = Conversation
    fields = ('content', 'role', 'call_session', 'system_topic', 'personal_topic', 'postfix', 'save_time',
              'created_at', 'updated_at')
    readonly_fields = ('content', 'role', 'call_session', 'system_topic', 'personal_topic', 'save_time', 'postfix', 'created_at',
                       'updated_at')
    extra = 0
    ordering = ('save_time',)


class CallSessionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'direction', 'start_time', 'end_time', 'audio', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'phone_number', 'start_time', 'end_time', 'system_prompt')
    inlines = [
        ConversationInline
    ]


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('call_session', 'role', 'content', 'save_time', 'created_at', 'updated_at', 'system_topic', 'personal_topic',
                    'audio', 'postfix')
    readonly_fields = ('call_session', 'role', 'content', 'created_at', 'updated_at', 'system_topic', 'personal_topic',
                       'save_time', 'audio', 'postfix')
    extra = 0
    ordering = ('-save_time',)


admin.site.register(CallSession, CallSessionAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(DigitalPersona)
admin.site.register(Biography)
