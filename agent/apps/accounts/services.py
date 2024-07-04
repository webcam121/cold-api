from datetime import timedelta

from django.utils import timezone
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

import django_rest_passwordreset
from django.conf import settings
from django_rest_passwordreset.models import get_password_reset_lookup_field, ResetPasswordToken
from rest_framework import exceptions


def generate_reset_pwd_token(email, user_agent='', ip_address=''):
    from .models import CustomUser

    # find a user by email address (case insensitive search)
    users = CustomUser.objects.filter(**{'{}__iexact'.format(get_password_reset_lookup_field()): email})

    active_user_found = False

    # iterate over all users and check if there is any user that is active
    # also check whether the password can be changed (is useable), as there could be users that are not allowed
    # to change their password (e.g., LDAP user)
    for user in users:
        if user.eligible_for_reset():
            active_user_found = True
            break

    # No active user found, raise a validation error
    # but not if DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE == True
    if not active_user_found and not getattr(settings, 'DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE', False):
        raise exceptions.ValidationError(
            {
                'email': [
                    "We couldn't find an account associated with that email. Please try a different e-mail address."
                ],
            }
        )

    # last but not least: iterate over all users that are active and can change their password
    # and create a Reset Password Token and send a signal with the created token
    for user in users:
        if user.eligible_for_reset():
            # check if the user already has a token
            if user.password_reset_tokens.all().count() > 0:
                # yes, already has a token, re-use this token
                return user.password_reset_tokens.all()[0]
            # no token exists, generate a new token
            return ResetPasswordToken.objects.create(
                user=user,
                user_agent=user_agent,
                ip_address=ip_address,
            )


def clear_expired_tokens():
    """
    Delete all existing expired tokens
    """
    password_reset_token_validation_time = django_rest_passwordreset.models.get_password_reset_token_expiry_time()

    # datetime.now minus expiry hours
    now_minus_expiry_time = timezone.now() - timedelta(hours=password_reset_token_validation_time)

    # delete all tokens where created_at < now - 24 hours
    django_rest_passwordreset.models.clear_expired(now_minus_expiry_time)


def check_unsub_token(email, token):
    try:
        key = '%s:%s' % (email, token)
        TimestampSigner().unsign(key)
    except (BadSignature, SignatureExpired):
        return False
    return True
