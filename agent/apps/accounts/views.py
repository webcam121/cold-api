import logging
from datetime import datetime, timedelta

from dj_rest_auth.registration.views import LoginView, RegisterView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import ResetPasswordRequestToken, HTTP_USER_AGENT_HEADER, HTTP_IP_ADDRESS_HEADER
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_rest_passwordreset.serializers import EmailSerializer


from agent.apps.accounts.models import GiftReceiver, CustomUser, GiftGiver, Prereceiver, InvitationToken, \
    ExpiringAuthToken, DailyUpdate
from agent.apps.accounts.permissions import IsGiftGiver, APIKeyPermission, IsGiftReceiver, IsGiverOfReceiver, \
    IsGiverOfPreReceiver
from agent.apps.accounts.serializers import CustomLoginSerializer, CustomRegisterWithPasswordSerializer, \
    GiftReceiverSerializer, UserProfileImageUpdateSerializer, UserProfileNameUpdateSerializer, \
    UserProfileUpdateSerializer, \
    CustomUserSerializer, SetUserPasswordSerializer, RegisterPreGiftReceiverSerializer, PreGiftReceiverSerializer, \
    PreReceiverUpdateSerializer, PrereceiverSerializer, InviteUserSerializer, AcceptInvitationSerializer, \
    RetrievePreGiftReceiverSerializer, DailyUpdateModifySerializer, ListGiftReceiverSerializer
from agent.apps.accounts.services import check_unsub_token
from agent.apps.accounts.tasks import send_invitation_email_to_user_from_giver, \
    send_invitation_email_to_nonuser_from_giver, send_invitation_email_to_user_from_receiver, \
    send_invitation_email_to_nonuser_from_receiver

from agent.authentication import ExpiringTokenAuthentication

logger = logging.getLogger('login')


class CustomRegisterView(RegisterView):
    def create(self, request, *args, **kwargs):
        if settings.ENVIRONMENT == 'production':
            try:
                if self.request.data.get('first_name') == 'null' or self.request.data.get('last_name') == 'null':
                    logger.info(f'signup request: {self.request.headers} data: {self.request.data}')
            except Exception:
                pass
        response = super().create(request, *args, **kwargs)
        return response


class CustomLoginView(LoginView):
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()

        # Updating the response to include `is_giver`
        response = self.get_response()
        if getattr(self.user, 'is_giver', None) is not None:
            response.data.update({
                "is_giver": self.user.is_giver,
                "is_receiver": self.user.is_receiver,
                "image_url": self.user.image.url if self.user.image else None
            })
        return response


class CustomRegisterWithPasswordView(RegisterView):
    serializer_class = CustomRegisterWithPasswordSerializer


class AuthenticationTokenView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, *args, **kwargs):
        if self.request.auth:
            if self.request.user is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            refresh = RefreshToken.for_user(self.request.user)
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ListGiftReceiverView(APIView):
    serializer_class = ListGiftReceiverSerializer
    permission_classes = [IsAuthenticated, IsGiftGiver]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def get_queryset(self):
        gift_giver_user = self.request.user
        gift_giver = GiftGiver.objects.filter(user=gift_giver_user).first()
        return GiftReceiver.objects.filter(gift_giver=gift_giver)


class ListPreReceiverView(APIView):
    serializer_class = PreGiftReceiverSerializer
    permission_classes = [IsAuthenticated, IsGiftGiver]
    queryset = Prereceiver.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        gift_giver_user = CustomUser.objects.get(id=self.request.user.id)
        gift_giver = GiftGiver.objects.get(user=gift_giver_user)
        return self.queryset.filter(giver=gift_giver)


class DetailGiftReceiverView(generics.RetrieveDestroyAPIView):
    serializer_class = GiftReceiverSerializer
    permission_classes = [IsAuthenticated, IsGiftGiver, IsGiverOfReceiver]
    queryset = GiftReceiver.objects.all()


class DetailPreGiftReceiverView(generics.RetrieveDestroyAPIView):
    serializer_class = PreGiftReceiverSerializer
    permission_classes = [IsAuthenticated, IsGiftGiver, IsGiverOfPreReceiver]
    queryset = Prereceiver.objects.all()


class DetailCallerPhoneNumberView(APIView):
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        phone_number = kwargs.get('phone_number')
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        res_data = {
            "first_name": user.first_name if user else "",
            "last_name": user.last_name if user else "",
            "phone_number": user.phone_number if user else None,
            "age": user.age if user else 45,
            "trivia": user.trivia if user else True,
        }
        return Response(res_data, status=status.HTTP_200_OK)


class DetailPreReceiverByGiverPhoneNumberView(generics.RetrieveAPIView):
    serializer_class = RetrievePreGiftReceiverSerializer
    queryset = Prereceiver.objects.all()
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        phone_number = kwargs.get('phone_number')
        gift_giver = GiftGiver.objects.filter(user__phone_number=phone_number).first()
        if gift_giver:
            queryset = self.get_queryset()
            pre_receiver = queryset.filter(giver=gift_giver).order_by('-created_at').first()
            if pre_receiver is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            res_data = {
                "first_name": pre_receiver.first_name if pre_receiver.first_name else "",
                "last_name": pre_receiver.last_name if pre_receiver.last_name else "",
                "phone_number": pre_receiver.phone_number if pre_receiver.phone_number else "",
                "age": pre_receiver.age if pre_receiver.age else 45,
                "trivia": pre_receiver.receiver.user.trivia
            }
        else:
            res_data = {
                "first_name": "",
                "last_name": "",
                "phone_number": "",
                "age": 45,
                "trivia": True
            }
        return Response(res_data, status=status.HTTP_200_OK)

      
class SkipTriviaGameView(APIView):
    permission_classes = [APIKeyPermission]
    queryset = CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        phone_number = kwargs.get('phone_number')
        user = self.queryset.filter(phone_number=phone_number).first()
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user.trivia = False
            user.save()
            return Response(status=status.HTTP_200_OK)



class TrialDetailGiftReceiverByPhoneNumberView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        phone_number = kwargs.get('phone_number')
        queryset = self.get_queryset()
        user = queryset.filter(phone_number=phone_number).first()
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(user)
        return Response(serializer.data)


# class RegisterGiftReceiverView(APIView):
#     serializer_class = RegisterGiftReceiverSerializer
#     permission_classes = [IsAuthenticated, IsGiftGiver]
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             first_name = serializer.validated_data['first_name']
#             last_name = serializer.validated_data['last_name']
#             phone_number = serializer.validated_data.get('phone_number', None)
#             gender = serializer.validated_data.get('gender', None)
#             age = serializer.validated_data.get('age', None)
#
#             # Check if gift receiver exists with the same email
#             receiver_exists = GiftReceiver.objects.filter(user__email=email).exists()
#             if receiver_exists:
#                 # if email == self.request.user.email:
#                 #     return Response({'message': f"{email} is already on Agent. Ask them to share their stories with you!"})
#                 # else:
#                 return Response({'message':  f"{email} is already on Agent. Ask them to share their stories with you!"})
#
#             # Check if user exists with the same email
#             user_exists = CustomUser.objects.filter(email=email).exists()
#             if user_exists:
#                 custom_user = CustomUser.objects.get(email=email)
#                 custom_user.is_receiver = True
#                 custom_user.save()
#                 gift_giver = GiftGiver.objects.get(user__id=self.request.user.id)
#                 gift_receiver = GiftReceiver.objects.get(user=custom_user)
#                 gift_receiver.gift_giver.add(gift_giver)
#                 return Response({'pk': gift_receiver.pk}, status=status.HTTP_201_CREATED)
#
#             # If user does not exist
#             try:
#                 custom_user = CustomUser.objects.create(email=email, first_name=first_name, last_name=last_name,
#                                                         phone_number=phone_number, gender=gender, age=age,
#                                                         is_giver=False, is_receiver=True)
#                 gift_giver_user = CustomUser.objects.get(id=self.request.user.id)
#                 gift_giver = GiftGiver.objects.get(user=gift_giver_user)
#                 gift_receiver = GiftReceiver.objects.get(user=custom_user)
#                 gift_receiver.gift_giver.add(gift_giver)
#
#                 return Response({'pk': gift_receiver.pk}, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterPreGiftReceiverView(APIView):
    serializer_class = RegisterPreGiftReceiverSerializer
    permission_classes = [IsAuthenticated, IsGiftGiver]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            phone_number = serializer.validated_data.get('phone_number', None)
            gender = serializer.validated_data.get('gender', None)
            age = serializer.validated_data.get('age', None)

            # Check if gift receiver exists with the same email
            receiver_exists = GiftReceiver.objects.filter(user__email=email).exists()
            if receiver_exists:
                # Check if the phone number is also matching
                if phone_number and GiftReceiver.objects.filter(user__email=email, user__phone_number=phone_number).exists():
                    return Response(
                        {'message': f"{email} and {phone_number} are already on Agent. "
                                    f"Ask them to share their stories with you!"})
                return Response({'message':  f"{email} is already on Agent. Ask them to share their stories with you!"})

            # Check if gift receiver exists with the same phone number
            phone_number_exists = GiftReceiver.objects.filter(user__phone_number=phone_number).exists()
            if phone_number and phone_number_exists:
                return Response(
                    {'message': f"{phone_number} is already on Agent. Ask them to share their stories with you!"})

            # Check if user exists with the same email: he is not receiver but giver
            user_exists = CustomUser.objects.filter(email=email).exists()
            if user_exists:
                # in case phone number is inputted but does not match with the existing user's number
                if phone_number and not CustomUser.objects.filter(email=email,
                                                                  phone_number=phone_number).exists():
                    user = CustomUser.objects.filter(email=email).first()
                    # If there is a user with same email but no phone number then it will not return error
                    if user.phone_number is not None:
                        return Response({'message': "The user is already on Agent!"})

            # Check if user exists with the same phone: he is not a receiver but giver
            phone_exists = CustomUser.objects.filter(phone_number=phone_number).exists()
            if phone_number and phone_exists:
                # in case phone number is inputted but does not match with the existing user's number
                if email and not CustomUser.objects.filter(email=email, phone_number=phone_number).exists():
                    return Response({'message': "The user is already on Agent!"})

            # Other cases and if user does not exist
            try:
                gift_giver_user = CustomUser.objects.get(id=self.request.user.id)
                gift_giver = get_object_or_404(GiftGiver, user=gift_giver_user)
                pre_receiver = Prereceiver.objects.create(email=email, first_name=first_name, last_name=last_name,
                                                          phone_number=phone_number, gender=gender, age=age,
                                                          giver=gift_giver)
                return Response({'pk': pre_receiver.pk}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileImageView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileImageUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileNameView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileNameUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateReceiver(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        receiver_id = kwargs.get('pk')
        receiver_user = CustomUser.objects.get(id=receiver_id)
        serializer = UserProfileUpdateSerializer(receiver_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePreReceiver(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = PreReceiverUpdateSerializer

    def post(self, request, *args, **kwargs):
        pre_receiver_id = kwargs.get('pk')
        pre_receiver_user = Prereceiver.objects.get(pk=pre_receiver_id)
        if pre_receiver_user.giver.user != request.user:
            return Response("You don't have permission to perform this action", status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(pre_receiver_user, data=request.data, partial=True)
        if serializer.is_valid():
            email = serializer.validated_data.get('email', None)
            phone_number = serializer.validated_data.get('phone_number', None)

            if email:
                # Check if gift receiver exists with the same email
                receiver_exists = GiftReceiver.objects.filter(user__email=email).exists()
                if receiver_exists:
                    # Check if the phone number is also matching
                    if phone_number and GiftReceiver.objects.filter(user__email=email,
                                                                    user__phone_number=phone_number).exists():
                        return Response(
                            {'message': f"{email} and {phone_number} are already on Agent. "
                                        f"Ask them to share their stories with you!"})
                    return Response(
                        {'message': f"{email} is already on Agent. Ask them to share their stories with you!"})

                # Check if gift receiver exists with the same phone number
                phone_number_exists = GiftReceiver.objects.filter(user__phone_number=phone_number).exists()
                if phone_number and phone_number_exists:
                    return Response(
                        {'message': f"{phone_number} is already on Agent. Ask them to share their stories with you!"})

                # Check if user exists with the same email: he is not receiver but giver
                user_exists = CustomUser.objects.filter(email=email).exists()
                if user_exists:
                    # in case phone number is inputted but does not match with the existing user's number
                    if phone_number and not CustomUser.objects.filter(email=email,
                                                                      phone_number=phone_number).exists():
                        user = CustomUser.objects.filter(email=email).first()
                        # If there is a user with same email but no phone number then it will not return error
                        if user.phone_number is not None:
                            return Response({'message': "The user is already on Agent!"})

                # Check if user exists with the same phone: he is not a receiver but giver
                phone_exists = CustomUser.objects.filter(phone_number=phone_number).exists()
                if phone_number and phone_exists:
                    # in case phone number is inputted but does not match with the existing user's number
                    if email and not CustomUser.objects.filter(email=email, phone_number=phone_number).exists():
                        return Response({'message': "The user is already on Agent!"})

                # Save the updated data
                serializer.save()
                return Response({'message': 'Pre-receiver details updated successfully!'})
            else:
                # Save the updated data
                serializer.save()
                return Response({'message': 'Pre-receiver details updated successfully!'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckEmailExists(APIView):

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email:
            user_exists = CustomUser.objects.filter(email=email).exists()
            return Response({'email_exists': user_exists}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)


class CustomResetPasswordRequestTokenView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(CustomUser, email=email)
            token = ResetPasswordToken.objects.create(
                user=user,
                user_agent=request.META.get(HTTP_USER_AGENT_HEADER, ''),
                ip_address=request.META.get(HTTP_IP_ADDRESS_HEADER, ''),
            )
            return Response({"reset_password_token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailPaidGiverByReceiverPhoneNumberView(APIView):
    permission_classes = [APIKeyPermission]

    def get(self, request, *args, **kwargs):
        phone_number = kwargs.get("phone_number")
        user = get_object_or_404(CustomUser, phone_number=phone_number)

        # Retrieve the giver user associated with the active user plan
        giver_detail = {
            "first_name": user.first_name if user.first_name else "",
            "last_name": user.last_name if user.last_name else "",
            "phone_number": user.phone_number if user.phone_number else "",
            "age": user.age if user.age else 45
        }

        return Response(giver_detail, status=status.HTTP_200_OK)


class SetUserPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SetUserPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            password = serializer.validated_data['password']
            user.set_password(password)
            user.save(update_fields=['password'])  # Ensure only password field is updated
            return Response({'message': 'Password set successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUnsubscribeView(APIView):
    def get(self, request, *args, **kwargs):
        email = kwargs.get('email')
        unsub_token = kwargs.get('unsub_token')
        if check_unsub_token(email, unsub_token):
            user = CustomUser.objects.get(email=email)
            user.unsubscribed = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RetrieveMostRecentPreReceiver(APIView):
    permission_classes = [IsAuthenticated, IsGiftGiver]
    serializer_class = PrereceiverSerializer

    def get(self, request):
        giver_user = self.request.user
        gift_giver = get_object_or_404(GiftGiver, user=giver_user)

        # Retrieve the latest Prereceiver registered by the GiftGiver
        latest_prereceivers = Prereceiver.objects.filter(giver=gift_giver).order_by('-created_at').all()
        latest_prereceiver = None
        # Find non-paid latest pre-receiver
        for prereceiver in latest_prereceivers:
            if not prereceiver.pre_receiver_plans.filter(status='active').exists():
                latest_prereceiver = prereceiver
                break

        if latest_prereceiver:
            serializer = self.serializer_class(latest_prereceiver)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No non paid pre-receiver found for the gift giver'}, status=status.HTTP_404_NOT_FOUND)


class InviteUserForReceiverView(APIView):
    permission_classes = [IsAuthenticated, IsGiftReceiver]
    serializer_class = InviteUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            receiver_user = request.user
            gift_receiver = get_object_or_404(GiftReceiver, user=receiver_user)

            email = serializer.validated_data['email']
            daily_update = serializer.validated_data.get('daily_update', False)  # Default to False if not provided
            first_name = serializer.validated_data.get('first_name', None)
            last_name = serializer.validated_data.get('last_name', None)
            phone_number = serializer.validated_data.get('phone_number', None)
            custom_user = CustomUser.objects.filter(email=email).first()
            # In case the user already exists on Agent
            if custom_user:
                # Make the custom user as giver for any case
                custom_user.is_giver = True
                custom_user.save()

                # Make the user as giver of the receiver
                new_giver = GiftGiver.objects.filter(user=custom_user).first()
                gift_receiver.gift_giver.add(new_giver)
                gift_receiver.save()

                daily_update_obj, created = DailyUpdate.objects.get_or_create(gift_giver=new_giver, gift_receiver=gift_receiver)
                daily_update_obj.is_daily_update = daily_update
                daily_update_obj.save()
                # Send email notification
                send_invitation_email_to_user_from_receiver.delay(user_id=custom_user.pk, receiver_id=gift_receiver.pk, daily_update=daily_update)
                return Response(status=status.HTTP_200_OK)
            else:
                # Send email notification
                send_invitation_email_to_nonuser_from_receiver.delay(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number, receiver_id=gift_receiver.pk, daily_update=daily_update)
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)