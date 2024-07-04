from django.core.signing import TimestampSigner


def create_unsubscribe_link_token(email):
    email, token = make_unsub_token(email).split(":", 1)
    return email, token


def make_unsub_token(email):
    return TimestampSigner().sign(email)
