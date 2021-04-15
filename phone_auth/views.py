from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
)
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import FormView

from phone_auth.mixins import AnonymousRequiredMixin

from . import app_settings
from .forms import (
    AddEmailForm,
    AddPhoneForm,
    PhoneEmailVerificationForm,
    PhoneLoginForm,
    PhoneLogoutForm,
    PhonePasswordResetForm,
    PhoneRegisterForm,
)
from .models import EmailAddress, PhoneNumber
from .tokens import phone_token_generator


class PhoneSignupView(AnonymousRequiredMixin, FormView):
    """Display the register form and handle user registration."""

    form_class = PhoneRegisterForm
    template_name = "phone_auth/signup.html"
    success_url = reverse_lazy("phone_auth:phone_login")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(PhoneSignupView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        if form.errors:
            return render(self.request, self.template_name, context={"form": form})
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PhoneLoginView(AnonymousRequiredMixin, LoginView):
    """Display the login form and handle the login action."""

    form_class = PhoneLoginForm
    template_name = "phone_auth/login.html"

    def form_valid(self, form):
        """Security check complete. Log the user in."""

        user = authenticate(self.request, **form.cleaned_data)
        if user is not None:
            login(self.request, user)
        else:
            form.add_error("login", "Invalid Credentials")
            return render(
                self.request,
                "phone_auth/login.html",
                context={"form": form},
                status=400,
            )
        return HttpResponseRedirect(self.get_success_url())


class PhoneLogoutView(FormView):
    """Handle logout"""

    template_name = "phone_auth/logout.html"
    form_class = PhoneLogoutForm
    success_url = _(app_settings.LOGOUT_REDIRECT_URL)

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_logout(self.request)
        return super().form_valid(form)


class PhonePasswordResetView(FormView):
    """Display the password reset form and handle password reset using phone/email."""

    form_class = PhonePasswordResetForm
    template_name = "phone_auth/password_reset.html"
    success_url = reverse_lazy("phone_auth:phone_password_reset_done")

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PhonePasswordResetDoneView(PasswordResetDoneView):
    """Renders a template."""

    template_name = "phone_auth/password_reset_done.html"


class PhonePasswordConfirmView(PasswordResetConfirmView):
    """Accepts `uidb64` and `token` kwargs and validates them.

    If valid, it renders a form for the user to reset the password.
    """

    template_name = "phone_auth/password_reset_confirm.html"
    success_url = reverse_lazy("phone_auth:phone_password_reset_complete")


class PhonePasswordResetCompleteView(PasswordResetCompleteView):
    """Renders a template"""

    template_name = "phone_auth/password_reset_complete.html"


class PhoneChangePasswordView(PasswordChangeView):
    """View to change password using old password"""

    template_name = "phone_auth/change_password.html"
    success_url = reverse_lazy("phone_auth:phone_change_password_done")


class PhoneChangePasswordDoneView(PasswordChangeDoneView):
    """Renders a template"""

    template_name = "phone_auth/change_password_done.html"


class PhoneEmailVerificationView(LoginRequiredMixin, FormView):
    """
    Display all email-addresses and phone-numbers associated with user
    account with verification status on GET request.
    """

    template_name = "phone_auth/phone_and_email_verification.html"
    form_class = PhoneEmailVerificationForm
    title = None

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PhoneEmailVerificationView, self).get_context_data()
        context.update(
            {
                "email_addresses": self.request.user.emailaddress_set.all(),
                "phone_numbers": self.request.user.phonenumber_set.all(),
            }
        )
        if self.title is not None:
            context["title"] = self.title
        return context

    def form_valid(self, form):
        self.title = form.save(self.request.user)
        return render(
            self.request,
            template_name=self.template_name,
            context=self.get_context_data(),
        )


class PhoneEmailVerificationConfirmView(FormView):
    """Accepts `idb64` and `token` kwargs and validates them.

    If valid, it set is_verified to True of PhoneNumber/EmailAdress
    instance.
    """

    template_name = "phone_auth/phone_email_verification_confirm.html"

    # noinspection PyAttributeOutsideInit
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert "idb64" in kwargs and "token" in kwargs

        self.validlink = False
        email_obj, phone_obj = self.get_email_or_phone_obj(kwargs["idb64"])

        if email_obj is not None:
            user = email_obj.user
        elif phone_obj is not None:
            user = phone_obj.user
        else:
            user = None

        if user:
            is_valid_token = phone_token_generator(
                email_address_obj=email_obj, phone_number_obj=phone_obj
            ).check_token(user, kwargs["token"])

            if is_valid_token:
                if email_obj is not None:
                    email_obj.is_verified = True
                    email_obj.save()
                if phone_obj is not None:
                    phone_obj.is_verified = True
                    phone_obj.save()
                self.validlink = True

        # Display the "Verification Failed/Passed" page.
        return self.render_to_response(self.get_context_data())

    @staticmethod
    def get_email_or_phone_obj(idb64):
        email_obj = phone_obj = None
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(idb64).decode()
            method = uid[:5]
            pk = int(uid[5:])
            if method == "email":
                email_obj = EmailAddress.objects.get(pk=pk)
            elif uid[:5] == "phone":
                phone_obj = PhoneNumber.objects.get(pk=pk)

        except (
            TypeError,
            ValueError,
            OverflowError,
            EmailAddress.DoesNotExist,
            PhoneNumber.DoesNotExist,
            ValidationError,
        ):
            pass
        return email_obj, phone_obj

    def get_context_data(self, **kwargs):
        context = {}
        if self.validlink:
            context["title"] = _("Verification successful")
        else:
            context["title"] = _("Verification failed")
        return context


class AddPhoneView(LoginRequiredMixin, FormView):
    """Add new phone"""

    template_name = "phone_auth/add_new_phone.html"
    form_class = AddPhoneForm
    success_url = reverse_lazy("phone_auth:phone_email_verification")

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save(self.request.user)
        if form.errors:
            return render(self.request, self.template_name, context={"form": form})
        return super().form_valid(form)


class AddEmailView(LoginRequiredMixin, FormView):
    """Add new email"""

    template_name = "phone_auth/add_new_email.html"
    form_class = AddEmailForm
    success_url = reverse_lazy("phone_auth:phone_email_verification")

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save(self.request.user)
        if form.errors:
            return render(self.request, self.template_name, context={"form": form})
        return super().form_valid(form)
