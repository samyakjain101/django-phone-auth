from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from phone_auth.utils import login_method_allow

from .forms import (EmailValidationForm, PhoneValidationForm,
                    UsernameValidationForm)

User = get_user_model()


class CustomAuthBackend(ModelBackend):

    def authenticate(self, request, login=None, password=None, **kwargs):

        if login and password:

            lookup_obj = Q()

            if (login_method_allow('phone') and
                    PhoneValidationForm({'phone': login}).is_valid()):
                lookup_obj |= Q(phonenumber__phone=login)

            elif (login_method_allow('email') and
                    EmailValidationForm({'email': login}).is_valid()):
                lookup_obj |= Q(emailaddress__email=login)

            elif (login_method_allow('username') and
                    UsernameValidationForm({'username': login}).is_valid()):
                lookup_obj |= Q(username=login)

            else:
                return None

            if lookup_obj:
                try:
                    user = User.objects.get(lookup_obj)
                    if (user.check_password(password)
                            and self.user_can_authenticate(user)):
                        return user
                except User.DoesNotExist:
                    return None

        return None
