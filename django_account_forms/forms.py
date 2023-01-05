from typing import Type

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm, UserCreationForm, \
    PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from django.conf import settings as django_settings
from django_account_forms.utils import generate_token, get_token_payload
from .models import UserStatus
from .settings import AppSettings

User = get_user_model()
app_settings = AppSettings()


class CreateAccountForm(UserCreationForm):
    class Meta:
        model = User
        fields = (User.USERNAME_FIELD, *app_settings.CREATE_ACCOUNT_FORM_FIELDS)

    def save(self, commit=True):
        user = super().save(commit=commit)
        user_status: UserStatus = UserStatus.objects.get(user=user)

        settings = AppSettings()

        if settings.AUTO_VERIFY_ACCOUNT:
            user_status.verified = True

        else:
            user_status.send_verification_email()

        user_status.save()
        return user


class VerifyAccountForm(forms.Form):
    token = forms.CharField()

    def save(self, ):
        settings = AppSettings()
        token = self.data['token']
        token_payload = get_token_payload(token, settings.VERIFICATION_TOKEN_MAX_AGE)
        username = token_payload[User.USERNAME_FIELD]
        user = User.objects.get(**{User.USERNAME_FIELD: username})
        status = user.status
        status.verified = True
        status.save()
        return user


class UpdateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = app_settings.UPDATE_ACCOUNT_FORM_FIELDS


class PasswordChangeForm(BasePasswordChangeForm):
    error_messages = {
        **BasePasswordChangeForm.error_messages,
        "same_password": _(
            "Your new password was the old password."
        ),
    }

    def clean_new_password1(self):
        """
        Validate that the new password is not the same.
        """
        new_password = self.cleaned_data["new_password1"]

        if self.user.check_password(new_password):
            raise ValidationError(
                self.error_messages["same_password"],
                code="same_password",
            )
        return new_password


class PasswordResetForm(BasePasswordResetForm):
    def save(self):
        return super().save(domain_override=app_settings.CLIENT_APP_DOMAIN,
                            subject_template_name=app_settings.PASSWORD_RESET_SUBJECT_TEMPLATE,
                            email_template_name=app_settings.PASSWORD_RESET_BODY_TEMPLATE,
                            use_https=app_settings.CLIENT_APP_USE_HTTPS)


class ConfirmPasswordResetForm(PasswordChangeForm):
    old_password = None
    token = forms.CharField()

    field_order = ["new_password1", "new_password2"]

    error_messages = {
        **PasswordChangeForm.error_messages,
        "invalid_token": _(
            "Your provided token was invalid."
        ),
    }

    def clean_token(self):
        token = self.cleaned_data["token"]

        if default_token_generator.check_token(self.user, token):
            return token

        else:
            raise ValidationError(
                self.error_messages["invalid_token"],
                code="invalid_token",
            )


class BlockUserForm(forms.Form):
    user = None
    user_id = forms.IntegerField()

    error_messages = {
        "user_doesnt_exist": _(
            "User with this is does not exist."
        ),
        "user_already_blocked": _(
            "User is already blocked."
        ),
    }

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = User.objects.select_related('status').get(id=user_id)

            if user.status.blocked is False:
                self.user = user
                return user_id
            else:
                raise ValidationError(
                    self.error_messages["user_already_blocked"],
                    code="user_already_blocked",
                )
        except ObjectDoesNotExist:
            raise ValidationError(
                self.error_messages["user_doesnt_exist"],
                code="user_doesnt_exist",
            )

    def save(self, ):
        status = self.user.status
        status.blocked = True
        status.save()
        return self.user


class UnblockUserForm(forms.Form):
    user = None
    user_id = forms.IntegerField()

    error_messages = {
        "user_doesnt_exist": _(
            "User with this is does not exist."
        ),
        "user_is_not_blocked": _(
            "User is already blocked."
        ),
    }

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = User.objects.select_related('status').get(id=user_id)

            if user.status.blocked is True:
                self.user = user
                return user_id
            else:
                raise ValidationError(
                    self.error_messages["user_is_not_blocked"],
                    code="user_is_not_blocked",
                )
        except ObjectDoesNotExist:
            raise ValidationError(
                self.error_messages["user_doesnt_exist"],
                code="user_doesnt_exist",
            )

    def save(self, ):
        status = self.user.status
        status.blocked = False
        status.save()
        return self.user
