from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from agent.apps.accounts.models import ExpiringAuthToken


def is_token_expired(token):
    if token.expire_at:
        return timezone.now() > token.expire_at

    return timezone.now() > token.created_at + timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS)


class ExpiringTokenAuthentication(TokenAuthentication):
    """Same as in DRF, but also handle Token expiration.

    An expired Token will be removed and a new Token with a different
    key is created that the User can obtain by logging in with his
    credentials.

    Raise AuthenticationFailed as needed, which translates
    to a 401 status code automatically.
    https://stackoverflow.com/questions/14567586
    """

    def authenticate_credentials(self, key):
        try:
            token = ExpiringAuthToken.objects.get(key=key)
            user = token.user
            if user.is_staff and user.is_active:
                return user, token
        except ExpiringAuthToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        if not token.user.is_active:
            raise AuthenticationFailed("Invalid token")
        if is_token_expired(token):
            token.delete()
            raise AuthenticationFailed("Token has expired")

        return token.user, token
