from django.contrib.auth import get_user_model


class UserMixin:
    default_user_password = 'test_passworD'
    default_user_email = 'test@mail.com'
    user = None

    def create_user(self, **user_kwargs):
        password = user_kwargs.pop('password', self.default_user_password)
        email = user_kwargs.pop('email', self.default_user_email)

        user = get_user_model()(email=email, **user_kwargs)
        user.set_password(password)
        user.save()

        self.user = user
        return user
