from django.test import TestCase
from django_account_forms.forms import UnblockUserForm, BlockUserForm

from .mixins import UserMixin


class BlockUserTestCase(TestCase, UserMixin):
    def setUp(self):
        self.create_user()

    def test_user_successfully_blocked(self):
        self.assertFalse(self.user.status.blocked)

        form = BlockUserForm(data={'user_id': self.user.id})

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertTrue(user.status.blocked)

    def test_user_did_not_exist(self):
        form = BlockUserForm(data={'user_id': self.user.id + 3})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["user_id"][0].messages[0]
        self.assertEqual(message, BlockUserForm.error_messages["user_doesnt_exist"])

    def test_user_already_blocked(self):
        status = self.user.status
        status.blocked = True
        status.save()

        form = BlockUserForm(data={'user_id': self.user.id})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["user_id"][0].messages[0]
        self.assertEqual(message, BlockUserForm.error_messages["user_already_blocked"])


class UnblockUserTestCase(TestCase, UserMixin):
    def setUp(self):
        self.create_user()

    def test_user_successfully_blocked(self):
        status = self.user.status
        status.blocked = True
        status.save()

        form = UnblockUserForm(data={'user_id': self.user.id})

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertFalse(user.status.blocked)

    def test_user_did_not_exist(self):
        form = UnblockUserForm(data={'user_id': self.user.id + 3})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["user_id"][0].messages[0]
        self.assertEqual(message, UnblockUserForm.error_messages["user_doesnt_exist"])

    def test_user_is_not_blocked(self):
        status = self.user.status
        status.blocked = False
        status.save()

        form = UnblockUserForm(data={'user_id': self.user.id})

        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        message = errors["user_id"][0].messages[0]
        self.assertEqual(message, UnblockUserForm.error_messages["user_is_not_blocked"])
