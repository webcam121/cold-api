from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin
from rest_framework_simplejwt import token_blacklist

from agent.apps.accounts.models import CustomUser, ExpiringAuthToken, GiftGiver, GiftReceiver, ClientAPIKey, \
    Prereceiver, DailyUpdate
from agent.apps.call_schedules.models import CallSchedule
from agent.apps.call_sessions.models import CallSession
from agent.apps.questions.models import PersonalQuestion


class PersonalQuestionInline(admin.TabularInline):
    model = PersonalQuestion
    fields = ('question', 'covered', 'category')
    readonly_fields = ('created_at', 'updated_at', 'category')
    extra = 0


class GiftGiverAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    djangoql_completion_enabled_by_default = False
    list_display = (
        'get_email',
        'get_first_name',
        'get_last_name',
        'get_phone_number',
        'get_last_login',
    )
    readonly_fields = (
        'get_email',
        'get_first_name',
        'get_last_name',
        'get_phone_number',
        'get_referral_link',
        'get_origin_domain',
        'get_password',
        'get_password_updated_at',
        'get_last_login',
        'get_date_joined',
        'get_is_staff',
        'get_is_superuser',
    )
    exclude = ('user_permissions', 'groups', 'password', 'user')
    show_full_result_count = False
    search_fields = (
        '=user__email',
        '=user__first_name',
        '=user__last_name',
    )

    list_filter = (
        'user__is_superuser',
        'user__last_login',
    )

    # change_form_template = 'apps/accounts/admin/customuser_changeform.html'
    inlines = [
        PersonalQuestionInline,
    ]

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'Email'

    def get_first_name(self, obj):
        return obj.user.first_name

    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name

    get_last_name.short_description = 'Last Name'

    def get_last_login(self, obj):
        return obj.user.last_login

    get_last_login.short_description = 'Last Login'

    def get_referral_link(self, obj):
        return obj.user.referral_link

    get_referral_link.short_description = 'Referral Link'

    def get_origin_domain(self, obj):
        return obj.user.origin_domain

    get_origin_domain.short_description = 'Origin Domain'

    def get_password(self, obj):
        return obj.user.password

    get_password.short_description = 'Password'

    def get_password_updated_at(self, obj):
        return obj.user.password_updated_at

    get_password_updated_at.short_description = 'Password Updated At'

    def get_date_joined(self, obj):
        return obj.user.date_joined

    get_date_joined.short_description = 'Date Joined'

    def get_is_staff(self, obj):
        return obj.user.is_staff

    get_is_staff.short_description = 'Is Stuff'

    def get_is_superuser(self, obj):
        return obj.user.is_superuser

    get_is_superuser.short_description = 'Is Superuser'

    def get_phone_number(self, obj):
        pn = obj.user.phone_number
        return pn

    get_phone_number.short_description = 'Phone Number'

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     return actions


class ExpiringAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'expire_at')
    # autocomplete_fields = ['user']
    readonly_fields = ('key', 'expire_at', 'user')
    search_fields = ('user__email',)


class CustomUserAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    djangoql_completion_enabled_by_default = False
    list_display = (
        'email',
        'first_name',
        'last_name',
        'phone_number',
        'last_login',
    )
    readonly_fields = (
        'referral_link',
        'origin_domain',
        'password',
        'password_updated_at',
        'last_login',
        'date_joined',
        'is_staff',
        'is_superuser',
    )
    exclude = ('user_permissions', 'groups', 'password')
    show_full_result_count = False
    search_fields = (
        '=email',
        '=first_name',
        '=last_name',
    )

    list_filter = (
        'is_superuser',
        'last_login',
    )

    # def user_phone_number(self, obj):
    #     pn = obj.phone_number
    #     return f'{pn[:3]}-{pn[3:6]}-{pn[6:]}'
    #
    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     return actions


class GiftGiverInline(admin.TabularInline):
    model = GiftReceiver.gift_giver.through
    extra = 0


class CallSessionInline(admin.TabularInline):
    model = CallSession
    fields = ('audio', 'user', 'direction', 'start_time', 'end_time')
    readonly_fields = ('audio', 'user', 'direction', 'start_time', 'end_time')
    extra = 0


class CallSchedulesInline(admin.TabularInline):
    model = CallSchedule
    fields = ('receiver', 'started_at', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'receiver', 'started_at')
    extra = 0


class GiftReceiverAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    djangoql_completion_enabled_by_default = False
    filter_horizontal = ('gift_giver',)
    list_display = (
        'get_email',
        'get_first_name',
        'get_last_name',
        'get_phone_number',
        'get_last_login',
    )

    readonly_fields = (
        'get_email',
        'get_first_name',
        'get_last_name',
        'get_phone_number',
        'get_referral_link',
        'get_origin_domain',
        'get_password',
        'get_password_updated_at',
        'get_last_login',
        'get_date_joined',
        'get_is_staff',
        'get_is_superuser',
        'gift_giver'
    )
    exclude = ('user_permissions', 'groups', 'password', 'user')
    show_full_result_count = False
    search_fields = (
        '=user__email',
        '=user__first_name',
        '=user__last_name',
    )

    list_filter = (
        'user__last_login',
    )

    inlines = [
        CallSchedulesInline
    ]

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'Email'

    def get_first_name(self, obj):
        return obj.user.first_name

    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name

    get_last_name.short_description = 'Last Name'

    def get_last_login(self, obj):
        return obj.user.last_login

    get_last_login.short_description = 'Last Login'

    def get_referral_link(self, obj):
        return obj.user.referral_link

    get_referral_link.short_description = 'Referral Link'

    def get_origin_domain(self, obj):
        return obj.user.origin_domain

    get_origin_domain.short_description = 'Origin Domain'

    def get_password(self, obj):
        return obj.user.password

    get_password.short_description = 'Password'

    def get_password_updated_at(self, obj):
        return obj.user.password_updated_at

    get_password_updated_at.short_description = 'Password Updated At'

    def get_date_joined(self, obj):
        return obj.user.date_joined

    get_date_joined.short_description = 'Date Joined'

    def get_is_staff(self, obj):
        return obj.user.is_staff

    get_is_staff.short_description = 'Is Stuff'

    def get_is_superuser(self, obj):
        return obj.user.is_superuser

    get_is_superuser.short_description = 'Is Superuser'

    def get_phone_number(self, obj):
        pn = obj.user.phone_number
        return pn

    get_phone_number.short_description = 'Phone Number'

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     return actions


class PrereceiverAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'giver',
        'receiver'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'giver',
        'receiver',
    )


class DailyUpdateAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'gift_giver',
        'gift_receiver',
        'is_daily_update'
    )
    readonly_fields = (
        'gift_giver',
        'gift_receiver',
    )


class OutstandingTokenAdmin(token_blacklist.admin.OutstandingTokenAdmin):
    def has_delete_permission(self, *args, **kwargs):
        return True


admin.site.unregister(token_blacklist.models.OutstandingToken)
admin.site.register(token_blacklist.models.OutstandingToken, OutstandingTokenAdmin)

# Register your models here.
admin.site.register(GiftGiver, GiftGiverAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ExpiringAuthToken, ExpiringAuthTokenAdmin)
admin.site.register(GiftReceiver, GiftReceiverAdmin)
admin.site.register(ClientAPIKey)
admin.site.register(Prereceiver, PrereceiverAdmin)
admin.site.register(DailyUpdate, DailyUpdateAdmin)
