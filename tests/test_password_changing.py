from django.test import TestCase
from django_account_forms.forms import PasswordChangeForm
from .mixins import UserMixin


class UpdateAccountTestCase(TestCase, UserMixin):
    initial_password = 'initial_password'

    def setUp(self):
        self.create_user(password=self.initial_password)

    def test_password_correctly_changed(self):
        new_password1 = 'new_pAsss2'
        new_password2 = 'new_pAsss2'

        form = PasswordChangeForm(user=self.user, data={'old_password': self.initial_password,
                                                        'new_password1': new_password1,
                                                        'new_password2': new_password2})

        self.assertTrue(form.is_valid())

        form.save()
        self.assertTrue(self.user.check_password(new_password1))

    def test_old_password_was_wrong(self):
        new_password1 = 'new_pAsss2'
        new_password2 = 'new_pAsss2'

        form = PasswordChangeForm(user=self.user, data={'old_password': self.initial_password + '23',
                                                        'new_password1': new_password1,
                                                        'new_password2': new_password2})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["old_password"][0].messages[0]
        self.assertEqual(message, PasswordChangeForm.error_messages["password_incorrect"])

    def test_new_password_was_old_password(self):
        new_password1 = self.initial_password
        new_password2 = self.initial_password

        form = PasswordChangeForm(user=self.user, data={"old_password": self.initial_password,
                                                        "new_password1": new_password1,
                                                        "new_password2": new_password2})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["new_password1"][0].messages[0]
        self.assertEqual(message, PasswordChangeForm.error_messages["same_password"])

    def test_new_passwords_were_different(self):
        new_password1 = 'new_pAsss3'
        new_password2 = 'new_pAsss2'

        form = PasswordChangeForm(user=self.user, data={"old_password": self.initial_password,
                                                        "new_password1": new_password1,
                                                        "new_password2": new_password2})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["new_password2"][0].messages[0]
        self.assertEqual(message, PasswordChangeForm.error_messages["password_mismatch"])
