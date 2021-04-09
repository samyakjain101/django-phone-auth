from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class AnonymousRequiredMixin(AccessMixin):
    """Verify that the current user is anonymous."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return super().dispatch(request, *args, **kwargs)
        return redirect(settings.LOGIN_REDIRECT_URL if settings.LOGIN_REDIRECT_URL else "/")
