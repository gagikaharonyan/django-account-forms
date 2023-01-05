from datetime import timedelta

from django.core import signing


def generate_token(user):
    username = user.get_username()
    payload = {user.USERNAME_FIELD: username}

    return signing.dumps(payload)


def get_token_payload(token, exp=None):
    return signing.loads(token, max_age=exp)
