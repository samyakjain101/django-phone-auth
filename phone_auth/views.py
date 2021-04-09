from django.contrib.auth import authenticate, login
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView)
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
# from django.views.generic import View
from django.views.generic.edit import FormView

from phone_auth.mixins import AnonymousRequiredMixin

from .forms import PhoneLoginForm, PhonePasswordResetForm, PhoneRegisterForm

# from .forms import EmailValidationForm
# from .models import EmailAddress, PhoneNumber


class PhoneRegisterView(FormView):
    """Display the register form and handle user registration."""

    form_class = PhoneRegisterForm
    template_name = 'phone_auth/register.html'
    success_url = '/'

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(PhoneRegisterView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        if form.errors:
            return render(
                self.request, 'register.html', context={'form': form})
        return super().form_valid(form)


class PhoneLoginView(AnonymousRequiredMixin, LoginView):
    """Display the login form and handle the login action."""

    form_class = PhoneLoginForm
    template_name = 'phone_auth/login.html'

    def form_valid(self, form):
        """Security check complete. Log the user in."""

        user = authenticate(self.request, **form.cleaned_data)
        if user is not None:
            login(self.request, user)
        else:
            form.add_error('login', 'Invalid Credentials')
            return render(
                self.request, 'phone_auth/login.html', context={'form': form}, status=400)
        return HttpResponseRedirect(self.get_success_url())


class PhonePasswordResetView(FormView):
    """Display the password reset form and handle password reset using phone/email."""

    form_class = PhonePasswordResetForm
    template_name = 'phone_auth/password_reset.html'
    success_url = reverse_lazy('phone_auth:phone_password_reset_done')

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PhonePasswordResetDoneView(PasswordResetDoneView):
    """Renders a template."""

    template_name = 'phone_auth/password_reset_done.html'


class PhonePasswordConfirmView(PasswordResetConfirmView):
    """Accepts `uidb64` and `token` kwargs and validates them.

    If valid, it renders a form for the user to reset the password.
    """

    template_name = 'phone_auth/password_reset_confirm.html'
    success_url = reverse_lazy('phone_auth:phone_password_reset_complete')


class PhonePasswordResetCompleteView(PasswordResetCompleteView):
    """Renders a template"""

    template_name = 'phone_auth/password_reset_complete.html'


class PhoneChangePasswordView(PasswordChangeView):
    """View to change password using old password"""

    template_name = 'phone_auth/change_password.html'
    success_url = reverse_lazy('phone_auth:phone_change_password_done')


class PhoneChangePasswordDoneView(PasswordChangeDoneView):
    """Renders a template"""

    template_name = 'phone_auth/change_password_done.html'


# class PhoneAndEmailVerificationView(LoginRequiredMixin, View):
#     """Display all email-addresses and phone-numbers associated with user
#     account with verification status.
#     """
#
#     template_name = 'phone_auth/phone_and_email_verification.html'
#
#     def get(self, request):
#         context = {
#             'email_addresses': self.request.user.emailaddress_set.all(),
#             'phone_numbers': self.request.user.phonenumber_set.all()
#         }
#         return render(request, template_name=self.template_name, context=context)
#
#     def post(self, request):
#
#         if request.POST.get('email', False):
#             form = EmailValidationForm(request.POST)
#
#             if form.is_valid():
#                 email = form.cleaned_data.get('email')
#                 try:
#                     email_obj = EmailAddress.objects.get(email__iexact=email)
#                     if email_obj.is_verified:
#                         return  # email is already verified
#
#                 except EmailAddress.DoesNotExist:
#                     # In this case say email sent successfully,
#                     # to avoid user enumeration attack
#                     pass
#
#         return render(request, template_name=self.template_name)
