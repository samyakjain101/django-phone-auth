import sys

from django.conf import settings

from .exceptions import AuthenticationMethodEmpty


class AppSettings:
    class AuthenticationMethod:
        USERNAME = "username"
        EMAIL = "email"
        PHONE = "phone"

    @property
    def AUTHENTICATION_METHODS(self):
        default = {
            self.AuthenticationMethod.USERNAME,
            self.AuthenticationMethod.EMAIL,
            self.AuthenticationMethod.PHONE,
        }
        auth_methods = self._setting("AUTHENTICATION_METHODS", default)
        if not auth_methods:
            raise AuthenticationMethodEmpty
        return auth_methods

    @property
    def REGISTER_USERNAME_REQUIRED(self):
        default = True
        return self._setting("REGISTER_USERNAME_REQUIRED", default)

    @property
    def REGISTER_EMAIL_REQUIRED(self):
        default = True
        return self._setting("REGISTER_EMAIL_REQUIRED", default)

    @property
    def REGISTER_FNAME_REQUIRED(self):
        default = True
        return self._setting("REGISTER_FNAME_REQUIRED", default)

    @property
    def REGISTER_LNAME_REQUIRED(self):
        default = True
        return self._setting("REGISTER_LNAME_REQUIRED", default)

    @property
    def REGISTER_CONFIRM_PASSWORD_REQUIRED(self):
        default = True
        return self._setting("REGISTER_CONFIRM_PASSWORD_REQUIRED", default)

    @property
    def LOGIN_REDIRECT_URL(self):
        default = "/accounts/profile/"
        return self._setting("LOGIN_REDIRECT_URL", default)

    @property
    def LOGOUT_REDIRECT_URL(self):
        default = "/"
        return self._setting("LOGOUT_REDIRECT_URL", default)

    @staticmethod
    def _setting(name, default):
        ret = getattr(settings, name, default)
        return ret if ret is not None else default


app_settings = AppSettings()
app_settings.__name__ = __name__
# noinspection PyTypeChecker
sys.modules[__name__] = app_settings
