from django.test import TestCase
from django_account_forms.forms import PasswordResetForm, ConfirmPasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from .mixins import UserMixin


class UpdateAccountTestCase(TestCase, UserMixin):
    initial_password = 'initial_password'

    def setUp(self):
        self.create_user(password=self.initial_password)

    def test_email_successfully_sent(self):
        form = PasswordResetForm(data={'email': self.default_user_email})

        self.assertTrue(form.is_valid())

        self.assertIsNone(form.save())

    def test_password_resetting_succeeded(self):
        new_password1 = 'new_pAsss2'
        new_password2 = 'new_pAsss2'

        token = default_token_generator.make_token(self.user)

        form = ConfirmPasswordResetForm(user=self.user, data={'token': token,
                                                              'new_password1': new_password1,
                                                              'new_password2': new_password2})

        self.assertTrue(form.is_valid())

        form.save()
        self.assertTrue(self.user.check_password(new_password1))

    def test_provided_toke_was_invalid(self):
        new_password1 = 'new_pAsss2'
        new_password2 = 'new_pAsss2'

        token = default_token_generator.make_token(self.user)

        form = ConfirmPasswordResetForm(user=self.user, data={'token': token + 'some_invalid_thing',
                                                              'new_password1': new_password1,
                                                              'new_password2': new_password2})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["token"][0].messages[0]
        self.assertEqual(message, ConfirmPasswordResetForm.error_messages["invalid_token"])

    def test_resetting_password_was_same(self):
        new_password1 = self.initial_password
        new_password2 = self.initial_password

        token = default_token_generator.make_token(self.user)

        form = ConfirmPasswordResetForm(user=self.user, data={'token': token,
                                                              'new_password1': new_password1,
                                                              'new_password2': new_password2})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["new_password1"][0].messages[0]
        self.assertEqual(message, ConfirmPasswordResetForm.error_messages["same_password"])
