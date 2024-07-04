from django.contrib import admin

from agent.apps.questions.models import PersonalQuestion, PersonalQuestionCategory, SystemQuestion, \
    CharacterLimitSetting, Node, Edge

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'label', 'content', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'label', 'source_node', 'target_node', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

class PersonalQuestionInline(admin.TabularInline):
    model = PersonalQuestion
    fields = ('question', 'covered', 'gift_giver')
    readonly_fields = ('created_at', 'updated_at', 'gift_giver')
    extra = 0


class PersonalQuestionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'question', 'covered', 'category', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'gift_giver', 'gift_receiver', 'pre_receiver')


class PersonalQuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'order', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class SystemQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'updated_at', 'category')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('question',)
    list_filter = ('category',)


@admin.register(CharacterLimitSetting)
class CharacterLimitSettingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'category', 'achievement_character_limit', 'unusual_character_limit',
        'noend_character_limit', 'verylong_character_limit',
        'controversial_character_limit', 'nontraditional_character_limit',
        'funny_character_limit', 'opinion_character_limit',
        'someonenew_character_limit', 'default_character_limit',
        'min_character', 'max_character',
        'number_q_topic_limit', 'total_number_topics_limit',
        'number_messages_cutoff', 'num_postfix_cutoff'
    ]


admin.site.register(SystemQuestion, SystemQuestionAdmin)
admin.site.register(PersonalQuestion, PersonalQuestionAdmin)
admin.site.register(PersonalQuestionCategory, PersonalQuestionCategoryAdmin)
