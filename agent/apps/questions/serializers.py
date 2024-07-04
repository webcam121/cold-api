from rest_framework import serializers

from agent.apps.accounts.models import GiftReceiver, GiftGiver, Prereceiver
from agent.apps.call_sessions.models import Conversation, ConversationTopicSummary
from agent.apps.questions.models import PersonalQuestion, PersonalQuestionCategory, SystemQuestion, \
    CharacterLimitSetting, Edge, Node


class NodeSerializer(serializers.ModelSerializer):
    edges = serializers.SerializerMethodField()
    class Meta:
        model = Node
        fields = ['id', 'content', 'edges']

    def get_edges(self, obj):
        edges = obj.source.all()
        return [{'id': edge.id, 'label': edge.label, 'target_node_id': edge.target_node.id, 'target_node_content': edge.target_node.content} for edge in edges]


class EdgeSerializer(serializers.ModelSerializer):
    target_node = NodeSerializer()
    class Meta:
        model = Edge
        fields = ['id', 'target_node', 'label']





class CharacterLimitSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterLimitSetting
        fields = '__all__'


class ListConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = ('id', 'created_at', 'updated_at', 'call_session', 'role', 'content', 'audio')


class ListTopicSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = ConversationTopicSummary
        fields = ('id', 'created_at', 'updated_at', 'summary', 'title', 'audio', 'share_link')


class ListPersonalQuestionSerializer(serializers.ModelSerializer):
    # conversation = serializers.SerializerMethodField()
    topic_summary = serializers.SerializerMethodField()

    class Meta:
        model = PersonalQuestion
        fields = ('pk', 'created_at', 'updated_at', 'question', 'covered', 'gift_giver', 'gift_receiver', 'category',
                  'topic_summary')
        extra_kwargs = {
            'gift_giver': {'read_only': True},
        }

    # def get_conversation(self, obj):
    #     conversation = obj.personal_conversations
    #     if conversation:
    #         return ListConversationSerializer(conversation, many=True).data
    #     return None

    def get_topic_summary(self, obj):
        summary = obj.personal_topic_summaries.order_by('-created_at').first()
        if summary:
            return [ListTopicSummarySerializer(summary).data]
        return None


class ListSystemQuestionSerializer(serializers.ModelSerializer):
    # conversation = serializers.SerializerMethodField()
    topic_summary = serializers.SerializerMethodField()

    class Meta:
        model = SystemQuestion
        fields = ('pk', 'created_at', 'updated_at', 'question', 'category', 'topic_summary')

    # def get_conversation(self, obj):
    #     receiver_id = self.context['receiver_id']
    #     conversation = obj.system_conversations.filter(call_session__receiver__user__id=receiver_id)
    #     if conversation:
    #         return ListConversationSerializer(conversation, many=True).data
    #     return None

    def get_topic_summary(self, obj):
        receiver_id = self.context['receiver_id']
        summary = obj.system_topic_summaries.filter(receiver__user__id=receiver_id).order_by('-created_at').first()
        if summary:
            return [ListTopicSummarySerializer(summary).data]
        return None


class ListSystemQuestionForNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemQuestion
        fields = ('pk', 'created_at', 'updated_at', 'question', 'category')


class CreatePersonalQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalQuestion
        fields = ('question', 'gift_receiver')

    def validate_gift_receiver(self, value):
        try:
            GiftReceiver.objects.get(pk=value)
        except GiftReceiver.DoesNotExist:
            raise serializers.ValidationError('Gift Receiver does not exist')
        return value


class CreatePreReceiverPersonalQuestionSerializer(serializers.ModelSerializer):
    pre_receiver_id = serializers.IntegerField(write_only=True)  # Serializer field for pre_receiver ID
    class Meta:
        model = PersonalQuestion
        fields = ('question', 'pre_receiver_id')

    def validate_pre_receiver_id(self, value):
        try:
            Prereceiver.objects.get(pk=value)
        except Prereceiver.DoesNotExist:
            raise serializers.ValidationError('Pre Receiver does not exist')
        return value


class UpdatePersonalQuestionSerializer(serializers.ModelSerializer):
    # Define a field for the question ID
    question_id = serializers.IntegerField()
    category_id = serializers.PrimaryKeyRelatedField(queryset=PersonalQuestionCategory.objects.all(),
                                                     allow_null=True, source='category', write_only=True)

    class Meta:
        model = PersonalQuestion
        fields = ('question_id', 'question', 'category_id',)


class PersonalQuestionCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalQuestionCategory
        fields = ('pk', 'created_at', 'updated_at', 'category')


class GiftGiverSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = GiftGiver
        fields = ['first_name', 'last_name']


class GiftReceiverSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = GiftReceiver
        fields = ['first_name', 'last_name']


class PersonalQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalQuestion
        fields = ['question', 'gift_giver', 'gift_receiver', 'category', 'covered']

        extra_kwargs = {
            'gift_giver': {'read_only': True}
        }


class ListCategoryPersonalQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalQuestion
        fields = ['pk', 'question', 'gift_giver', 'gift_receiver', 'pre_receiver', 'category', 'covered']


class SystemQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemQuestion
        fields = ['question',]


class SharedTopicSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = ConversationTopicSummary
        fields = ['summary', 'title', 'audio']


class LatestPersonalQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalQuestion
        fields = '__all__'
