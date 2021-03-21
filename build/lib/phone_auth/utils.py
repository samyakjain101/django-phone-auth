import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def get_setting(name, default=None):
    if name:
        try:
            return getattr(settings, name)
        except AttributeError:
            return default
    else:
        return default


def get_username_regex():
    """
    Username should be alphanumeric and in lowercase
    """
    return r'^[a-z0-9]{4,30}$'


def validate_username(username):
    if re.search(get_username_regex(), username) is None:
        raise ValidationError(
            _('%(username)s should be alphanumeric and in lowercase'),
            params={'username': username},
        )


class LOGIN_METHOD_EMPTY(Exception):
    """Exception raised if LOGIN_METHODS is set to
    empty set in settings

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="LOGIN_METHODS can't be empty"):
        self.message = message
        super().__init__(self.message)


def login_method_allow(method):
    LOGIN_METHODS = get_setting('LOGIN_METHODS', default={'phone'})
    if not LOGIN_METHODS:
        raise LOGIN_METHOD_EMPTY
    if method in LOGIN_METHODS:
        return True
    return False
