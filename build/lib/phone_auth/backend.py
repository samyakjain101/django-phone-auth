from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .forms import (
    PhoneValidationForm, EmailValidationForm,
    UsernameValidationForm)
from django.db.models import Q
from phone_auth.utils import login_method_allow

User = get_user_model()


class CustomAuthBackend(ModelBackend):

    def authenticate(self, request, login=None, password=None):

        if login and password:

            lookup_obj = Q()

            if (login_method_allow('email') and
                    EmailValidationForm({'email': login}).is_valid()):
                lookup_obj |= Q(email=login)

            if (login_method_allow('username') and
                    UsernameValidationForm({'username': login}).is_valid()):
                lookup_obj |= Q(username=login)

            if (login_method_allow('phone') and
                    PhoneValidationForm({'phone': login}).is_valid()):
                lookup_obj |= Q(phonenumber__phone=login)

            # By default email is set to unique=False. So,
            # multiple users may be returned. In this case,
            # first user which matches both email and password
            # will be returned
            if lookup_obj:
                users = User.objects.filter(lookup_obj)
                for user in users:
                    if (user.check_password(password)
                            and self.user_can_authenticate(user)):
                        return user
            return None

        return None
