import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def get_username_regex():
    """Username regex"""

    return r"^[a-zA-Z0-9_.-]{1,150}$"


def validate_username(username):
    if re.search(get_username_regex(), username) is None:
        raise ValidationError(
            _(
                "Username should be 150 characters or fewer."
                "Letters, digits and ./-/_ only."
            ),
            params={"username": username},
        )
