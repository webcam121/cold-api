from rest_framework import permissions

from agent.apps.accounts.models import GiftGiver, GiftReceiver


class IsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        gift_giver = GiftGiver.objects.filter(user=request.user).first()
        gift_receiver = GiftReceiver.objects.filter(user=request.user).first()
        if gift_receiver and obj.receiver == gift_receiver:
            return True
        elif gift_giver and obj.receiver.gift_giver.filter(user=request.user).exists():
            return True
        else:
            return False
