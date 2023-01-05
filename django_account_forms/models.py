from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.contrib.auth import get_user_model
from django.template import loader
from django_account_forms.settings import AppSettings
from django_account_forms.utils import generate_token


class UserStatus(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='status', )
    blocked = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def send_verification_email(self):
        context = {'token': generate_token(self.user)}
        settings = AppSettings()

        subject_template = settings.ACCOUNT_VERIFICATION_SUBJECT_TEMPLATE
        body_template_name = settings.ACCOUNT_VERIFICATION_BODY_TEMPLATE

        subject = loader.render_to_string(subject_template, context)
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(body_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, None, [self.user.email])

        email_message.send()
