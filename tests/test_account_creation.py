from django.contrib.auth import get_user_model
from django.test import TestCase
from django_account_forms.forms import CreateAccountForm, VerifyAccountForm, UpdateAccountForm
from django_account_forms.settings import override_settings
from django_account_forms.utils import generate_token
from .mixins import UserMixin

User = get_user_model()


class CreateAccountTestCase(TestCase, UserMixin):
    @override_settings({'AUTO_VERIFY_ACCOUNT': False})
    def test_user_correctly_created(self):
        email = 'test@gmail.com'
        password1 = 'PASS'
        password2 = 'PASS'
        form = CreateAccountForm(data={User.USERNAME_FIELD: email,
                                       'password1': password1,
                                       'password2': password2})

        self.assertTrue(form.is_valid())

        form.save()

        user = User.objects.get(**{User.USERNAME_FIELD: email, })
        self.assertTrue(user.check_password(password1))

    @override_settings({'AUTO_VERIFY_ACCOUNT': True})
    def test_user_correctly_created(self):
        email = 'test1@gmail.com'
        password1 = 'PASS'
        password2 = 'PASS'
        form = CreateAccountForm(data={User.USERNAME_FIELD: email,
                                       'password1': password1,
                                       'password2': password2})

        self.assertTrue(form.is_valid())

        form.save()

        user = User.objects.get(**{User.USERNAME_FIELD: email, })
        self.assertTrue(user.status.verified)

    def test_account_verified(self):
        user = self.create_user()
        status = user.status

        self.assertFalse(status.verified)

        token = generate_token(user)
        form = VerifyAccountForm(data={'token': token, })

        self.assertTrue(form.is_valid())

        user = form.save()
        status = user.status

        self.assertTrue(status.verified)

    def test_password_mismatch(self):
        email = 'test@gmail.com'
        password1 = 'PAST'
        password2 = 'PASS'
        form = CreateAccountForm(data={"email": email,
                                       "password1": password1,
                                       "password2": password2})

        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertEqual(errors["password2"][0].messages[0], CreateAccountForm.error_messages["password_mismatch"])

    def test_account_updated(self):
        first_name = 'test_name'
        user = self.create_user(username='second', first_name=first_name)

        self.assertEqual(user.first_name, first_name)

        edited_first_name = 'test_name_edited'
        form = UpdateAccountForm(data={'first_name': edited_first_name, })

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.first_name, edited_first_name)

