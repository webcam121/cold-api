from rest_framework import permissions

from agent.apps.accounts.models import CustomUser, GiftGiver, ClientAPIKey


class IsGiftGiver(permissions.BasePermission):

    def has_permission(self, request, view):
        req_user = CustomUser.objects.get(id=request.user.id)
        return req_user.is_giver

    def has_object_permission(self, request, view, obj):
        req_user = CustomUser.objects.get(id=request.user.id)
        return req_user.is_giver


class IsGiverOfReceiver(permissions.BasePermission):
    """
    Custom permission to only allow access to the receiver if the requesting user is the receiver's giver.
    """

    def has_object_permission(self, request, view, obj):

        # Check if the requesting user is the giver of the receiver
        return obj.gift_giver.filter(user=request.user).exists()


class IsGiverOfPreReceiver(permissions.BasePermission):
    """
    Custom permission to only allow access to the receiver if the requesting user is the receiver's giver.
    """

    def has_object_permission(self, request, view, obj):

        # Check if the requesting user is the giver of the receiver
        return obj.giver.user == request.user


class IsGiftReceiver(permissions.BasePermission):

    def has_permission(self, request, view):
        req_user = CustomUser.objects.get(id=request.user.id)
        return req_user.is_receiver

    def has_object_permission(self, request, view, obj):
        req_user = CustomUser.objects.get(id=request.user.id)
        return req_user.is_receiver


class APIKeyPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        api_key = request.headers.get('Authorization')

        if not api_key:
            return False

        try:
            client = ClientAPIKey.objects.get(api_key=api_key)
        except ClientAPIKey.DoesNotExist:
            return False

        return True
