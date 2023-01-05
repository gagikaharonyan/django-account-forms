from datetime import timedelta

from django.conf import settings as django_settings
from django.test import override_settings as django_override_settings


class Defaults:
    CLIENT_APP_DOMAIN = 'localhost:3000'
    CLIENT_APP_USE_HTTPS = True
    AUTO_VERIFY_ACCOUNT = False
    ACCOUNT_VERIFICATION_SUBJECT_TEMPLATE = 'email/password_reset_subject.txt'
    ACCOUNT_VERIFICATION_BODY_TEMPLATE = 'email/password_reset_body.html'
    PASSWORD_RESET_SUBJECT_TEMPLATE = 'email/password_reset_subject.txt'
    PASSWORD_RESET_BODY_TEMPLATE = 'email/password_reset_body.html'
    VERIFICATION_TOKEN_MAX_AGE = timedelta(hours=24)
    UPDATE_ACCOUNT_FORM_FIELDS = ('first_name', 'last_name',)
    CREATE_ACCOUNT_FORM_FIELDS = ('first_name', 'last_name',)


class AppSettings(Defaults):
    KEY_IN_SETTINGS = 'DJAGNO_ACCOUNT_FORMS'

    _user_settings = {}

    def __init__(self):
        self._user_settings = getattr(django_settings, self.KEY_IN_SETTINGS, {})

    def __getattribute__(self, attr):
        if hasattr(AppSettings, attr) is False:
            raise AttributeError("Invalid graphql_accounts setting: '%s'" % attr)

        try:
            val = object.__getattribute__(self, '_user_settings')[attr]
        except KeyError:
            val = object.__getattribute__(self, attr)

        return val


def override_settings(setting):
    return django_override_settings(**{AppSettings.KEY_IN_SETTINGS: setting})
