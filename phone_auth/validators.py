import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def get_username_regex():
    """Username should be alphanumeric and in lowercase"""

    return r'^[a-z0-9]{4,30}$'


def validate_username(username):
    if re.search(get_username_regex(), username) is None:
        raise ValidationError(
            _('%(username)s should be alphanumeric, lowercase and should\
            contain atleast 4 and atmost 30 characters'),
            params={'username': username},
        )
