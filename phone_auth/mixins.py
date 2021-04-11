from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class AnonymousRequiredMixin(AccessMixin):
    """Verify that the current user is anonymous."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return super().dispatch(request, *args, **kwargs)
        return redirect(settings.LOGIN_REDIRECT_URL if settings.LOGIN_REDIRECT_URL else "/")


class VerifiedPhoneRequiredMixin(AccessMixin):
    """Verify that the user has verified phone."""

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated and
                request.user.phonenumber_set.filter(is_verified=True).exists()):
            return super().dispatch(request, *args, **kwargs)
        return redirect('phone_auth:phone_email_verification')


class VerifiedEmailRequiredMixin(AccessMixin):
    """Verify that the user has verified email."""

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated and
                request.user.emailaddress_set.filter(is_verified=True).exists()):
            return super().dispatch(request, *args, **kwargs)
        return redirect('phone_auth:phone_email_verification')
