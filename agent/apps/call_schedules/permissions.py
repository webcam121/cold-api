from rest_framework import permissions

from agent.apps.accounts.models import GiftGiver, GiftReceiver


class IsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        receiver = GiftReceiver.objects.filter(user=request.user).first()
        return obj.receiver == receiver
