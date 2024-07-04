from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from rest_framework import serializers
from allauth.account.adapter import get_adapter
from allauth.account import app_settings as allauth_settings
from django.utils.translation import gettext_lazy as _

from agent.apps.accounts.models import CustomUser, GiftReceiver, Prereceiver, GiftGiver, DailyUpdate
from agent.services import cuttly_api


class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True, allow_blank=False)

    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        fields = ['email']


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta:
        model = CustomUser
        fields = ('pk', 'first_name', 'last_name', 'email', 'phone_number', 'is_giver', 'is_receiver', 'self_gift', 'last_login', 'date_joined')
        read_only_fields = ('email', 'last_login', 'date_joined')


class CustomRegisterWithPasswordSerializer(RegisterSerializer):
    GENDER_TYPE = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    username = None
    password2 = None
    password1 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=False)
    gender = serializers.ChoiceField(choices=GENDER_TYPE)
    age = serializers.IntegerField(required=False)

    def get_cleaned_data(self):
        super(CustomRegisterWithPasswordSerializer, self).get_cleaned_data()
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', None),
            'gender': self.validated_data.get('gender', None),
            'age': self.validated_data.get('age', None),
        }

    def custom_data(self, request):
        return {
            'origin_domain': self.validated_data.get('origin_domain', ''),
            'referral_link': cuttly_api.create_referral_link(email=request.data['email']),
        }

    def validate(self, data):
        return data

    def save(self, request):
        request.data._mutable = True
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        custom_data = self.custom_data(request)
        for k, v in custom_data.items():
            setattr(user, k, v)

        # Save additional fields to the user object
        user.phone_number = self.cleaned_data.get('phone_number')
        user.age = self.cleaned_data.get('age')
        user.gender = self.cleaned_data.get('gender')

        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        return user

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and CustomUser.objects.filter(email=email.lower()).exists():
                raise serializers.ValidationError(_("Email already registered"))
        return email


class CustomRegisterSerializer(RegisterSerializer):
    GENDER_TYPE = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    username = None
    password2 = None
    password1 = None
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    gender = serializers.ChoiceField(choices=GENDER_TYPE, required=False, allow_blank=True)
    age = serializers.IntegerField(required=False)
    self_gift = serializers.BooleanField(required=False)

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', None),
            'gender': self.validated_data.get('gender', None),
            'age': self.validated_data.get('age', None),
            'self_gift': self.validated_data.get('self_gift', False),
        }

    def validate(self, data):
        return data

    def custom_data(self, request):
        return {
            'origin_domain': self.validated_data.get('origin_domain', ''),
            'referral_link': cuttly_api.create_referral_link(email=request.data['email']),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        custom_data = self.custom_data(request)
        for k, v in custom_data.items():
            setattr(user, k, v)

        # Save additional fields to the user object
        user.phone_number = self.cleaned_data.get('phone_number')
        user.age = self.cleaned_data.get('age')
        user.gender = self.cleaned_data.get('gender')
        user.self_gift = self.cleaned_data.get('self_gift')

        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        return user

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and CustomUser.objects.filter(email=email.lower()).exists():
                raise serializers.ValidationError(_("Email already registered"))
        return email

    def validate_phone_number(self, phone_number):
        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError(_("Phone number already registered"))
        return phone_number


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'age')


class GiftReceiverSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = GiftReceiver
        fields = ('pk', 'user', 'gift_giver')


class ListGiftReceiverSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    is_daily_update = serializers.SerializerMethodField()

    class Meta:
        model = GiftReceiver
        fields = ('pk', 'user', 'gift_giver', 'is_daily_update')

    def get_is_daily_update(self, obj):
        user = self.context.get('request').user
        gift_giver = GiftGiver.objects.filter(user=user).first()
        if gift_giver:
            daily_update = DailyUpdate.objects.filter(gift_giver=gift_giver, gift_receiver=obj).first()
            return daily_update.is_daily_update if daily_update else False
        return False


class PreGiftReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prereceiver
        fields = ('pk', 'first_name', 'last_name', 'age', 'gender', 'email', 'phone_number', 'giver', 'created_at',
                  'updated_at')


class RetrievePreGiftReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prereceiver
        fields = ('first_name', 'last_name', 'phone_number', 'age')

# class RegisterGiftReceiverSerializer(serializers.Serializer):
#     GENDER_TYPE = [
#         ('M', 'Male'),
#         ('F', 'Female'),
#     ]
#
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)
#     email = serializers.EmailField(required=True)
#     phone_number = serializers.CharField(required=False)
#     gender = serializers.ChoiceField(choices=GENDER_TYPE, required=False)
#     age = serializers.IntegerField(required=False)


class RegisterPreGiftReceiverSerializer(serializers.Serializer):
    GENDER_TYPE = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=False)
    gender = serializers.ChoiceField(choices=GENDER_TYPE, required=False)
    age = serializers.IntegerField(required=False)


class UserProfileImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['image']


class UserProfileNameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'age', 'gender', 'image', 'phone_number', 'email']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and CustomUser.objects.filter(email=email.lower()).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(_("Email already registered"))
        return email

    def validate_phone_number(self, phone_number):
        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(_("Phone number already registered"))
        return phone_number


class PreReceiverUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prereceiver
        fields = ['first_name', 'last_name', 'age', 'gender', 'phone_number', 'email']


class SetUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, password):
        return get_adapter().clean_password(password)


class PrereceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prereceiver
        fields = '__all__'


class InviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    daily_update = serializers.BooleanField(required=False)


class AcceptInvitationSerializer(serializers.Serializer):
    invitation_token_key = serializers.CharField(required=True)


class DailyUpdateModifySerializer(serializers.Serializer):
    daily_update = serializers.BooleanField(required=True)
