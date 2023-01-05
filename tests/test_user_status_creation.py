from django.contrib.auth import get_user_model
from django.test import TestCase
from django_account_forms.models import UserStatus

from .mixins import UserMixin


class UserStatusTestCase(TestCase, UserMixin):
    User = get_user_model()

    # def setUp(self):
    #     Animal.objects.create(name="lion", sound="roar")
    #     Animal.objects.create(name="cat", sound="meow")

    def test_user_status_correctly_created(self):
        user = self.create_user()
        user_status = UserStatus.objects.get(user=user)

        self.assertTrue(user_status)
        self.assertEqual(user_status.user, user)
