from rest_framework import serializers
from .models import CallSession, Conversation, SystemPrompt, PostfixPrompt, DigitalPersona, Biography, TrialCallSession, TrialConversation
from ..questions.models import SystemQuestion, PersonalQuestion


class CallSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallSession
        fields = ('pk', 'start_time', 'end_time', 'phone_number', 'audio', 'summary', 'direction')


class TrialCallSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrialCallSession
        fields = ('pk', 'start_time', 'end_time', 'user', 'audio')


class StartCallSessionSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    direction = serializers.CharField(required=True)
    system_prompt = serializers.CharField(required=True)


class TrialStartCallSessionSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)


class ConversationSerializer(serializers.ModelSerializer):
    system_topic = serializers.PrimaryKeyRelatedField(queryset=SystemQuestion.objects.all(), allow_null=True, required=False)
    personal_topic = serializers.PrimaryKeyRelatedField(queryset=PersonalQuestion.objects.all(), allow_null=True, required=False)
    postfix = serializers.CharField(required=False)

    class Meta:
        model = Conversation
        fields = ['role', 'content', 'system_topic', 'personal_topic', 'postfix', 'audio', 'save_time']
        read_only_fields = ('audio',)



class TrialConversationSerializer(serializers.ModelSerializer):
    system_topic = serializers.PrimaryKeyRelatedField(queryset=SystemQuestion.objects.all(), allow_null=True, required=False)
    postfix = serializers.CharField(required=False)

    class Meta:
        model = TrialConversation
        fields = ['role', 'content', 'system_topic', 'postfix', 'audio', 'save_time']
        read_only_fields = ('audio',)


class SystemPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPrompt
        fields = '__all__'


class PostfixPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostfixPrompt
        fields = '__all__'


class DigitalPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalPersona
        fields = ['id', 'created_at', 'updated_at', 'digital_persona']


class BiographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = ['id', 'created_at', 'updated_at', 'biography']
