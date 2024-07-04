from rest_framework import permissions

from agent.apps.accounts.models import GiftGiver, CustomUser, GiftReceiver


class IsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        gift_giver = GiftGiver.objects.filter(user=request.user).first()
        gift_receiver = GiftReceiver.objects.filter(user=request.user).first()
        return obj.gift_giver == gift_giver or obj.gift_receiver == gift_receiver
