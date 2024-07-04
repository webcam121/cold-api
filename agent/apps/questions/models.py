from django.db import models
import uuid

from agent.apps.accounts.models import GiftGiver, GiftReceiver, Prereceiver


class PersonalQuestionCategory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=255, default='')
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.category

    class Meta:
        ordering = ['order']  # Specify the default ordering
        verbose_name = 'Personal Question Category'
        verbose_name_plural = 'Personal Question Categories'


class PersonalQuestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.TextField(null=False, blank=False)
    covered = models.BooleanField(default=False)
    gift_giver = models.ForeignKey(GiftGiver, on_delete=models.CASCADE, related_name='questions', null=False)
    gift_receiver = models.ForeignKey(GiftReceiver, on_delete=models.CASCADE, related_name='receiver_questions',
                                      null=True, blank=True)
    pre_receiver = models.ForeignKey(Prereceiver, on_delete=models.CASCADE, related_name='pre_receiver_questions',
                                     null=True, blank=True)
    category = models.ForeignKey(PersonalQuestionCategory, on_delete=models.CASCADE, related_name='category_questions',
                                 blank=True, null=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Personal Question'
        verbose_name_plural = 'Personal Questions'


class SystemQuestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.TextField(null=False, blank=False)
    rank = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(PersonalQuestionCategory, on_delete=models.CASCADE,
                                 related_name='category_system_questions', blank=True, null=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'System Question'
        verbose_name_plural = 'System Questions'


class CharacterLimitSetting(models.Model):
    CATEGORY_CHOICE = [
        ('trial', 'Trial'),
        ('default', 'Default'),
        ('notrivia', 'No Trivia')
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    achievement_character_limit = models.IntegerField(blank=True, null=True)
    unusual_character_limit = models.IntegerField(blank=True, null=True)
    noend_character_limit = models.IntegerField(blank=True, null=True)
    verylong_character_limit = models.IntegerField(blank=True, null=True)
    controversial_character_limit = models.IntegerField(blank=True, null=True)
    nontraditional_character_limit = models.IntegerField(blank=True, null=True)
    funny_character_limit = models.IntegerField(blank=True, null=True)
    opinion_character_limit = models.IntegerField(blank=True, null=True)
    someonenew_character_limit = models.IntegerField(blank=True, null=True)
    default_character_limit = models.IntegerField(blank=True, null=True)
    min_character = models.IntegerField(blank=True, null=True)
    max_character = models.IntegerField(blank=True, null=True)
    number_q_topic_limit = models.IntegerField(blank=True, null=True)
    total_number_topics_limit = models.IntegerField(blank=True, null=True)
    number_messages_cutoff = models.IntegerField(blank=True, null=True)
    num_postfix_cutoff = models.IntegerField(blank=True, null=True)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICE, default='default')

    def __str__(self):
        return "Character Limit Settings"

    class Meta:
        verbose_name = 'Character Limit Setting'
        verbose_name_plural = 'Character Limit Settings'


class Node(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    label = models.TextField(null=False, blank=False)
    content = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'


class Edge(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='source', null=False)
    target_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='target', null=False)
    label = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.source_node.label + ' -> ' + self.target_node.label

    class Meta:
        verbose_name = 'Edge'
        verbose_name_plural = 'Edges'
