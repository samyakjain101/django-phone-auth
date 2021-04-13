from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

from . import app_settings


class AnonymousRequiredMixin(AccessMixin):
    """Verify that the current user is anonymous."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return super().dispatch(request, *args, **kwargs)
        return redirect(app_settings.LOGIN_REDIRECT_URL)


class VerifiedPhoneRequiredMixin(AccessMixin):
    """Verify that the user has verified phone."""

    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.phonenumber_set.filter(is_verified=True).exists()
        ):
            return super().dispatch(request, *args, **kwargs)
        return redirect("phone_auth:phone_email_verification")


class VerifiedEmailRequiredMixin(AccessMixin):
    """Verify that the user has verified email."""

    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.emailaddress_set.filter(is_verified=True).exists()
        ):
            return super().dispatch(request, *args, **kwargs)
        return redirect("phone_auth:phone_email_verification")
