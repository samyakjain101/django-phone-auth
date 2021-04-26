from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from . import app_settings
from .app_settings import AuthenticationMethod
from .forms import EmailValidationForm, PhoneValidationForm, UsernameValidationForm

User = get_user_model()


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        """Authenticate with phone/email/username and password"""

        login = kwargs.get("login", kwargs.get("username", None))
        password = kwargs.get("password", None)

        if login and password:

            lookup_obj = Q()

            authentication_methods = app_settings.AUTHENTICATION_METHODS
            if (
                AuthenticationMethod.PHONE in authentication_methods
                and PhoneValidationForm({"phone": login}).is_valid()
            ):
                lookup_obj |= Q(phonenumber__phone=login)
            elif (
                AuthenticationMethod.EMAIL in authentication_methods
                and EmailValidationForm({"email": login}).is_valid()
            ):
                lookup_obj |= Q(emailaddress__email__iexact=login)
            elif (
                AuthenticationMethod.USERNAME in authentication_methods
                and UsernameValidationForm({"username": login}).is_valid()
            ):
                lookup_obj |= Q(username__exact=login)
            else:
                return None

            if lookup_obj:
                try:
                    user = User.objects.get(lookup_obj)
                    if user.check_password(password) and self.user_can_authenticate(
                        user
                    ):
                        return user
                except User.DoesNotExist:
                    return None

        return None
