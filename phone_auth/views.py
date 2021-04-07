from django.contrib.auth import authenticate, login
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView
)
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView

from .forms import LoginForm, PasswordResetForm, RegisterForm


class PhoneRegisterView(FormView):
    form_class = RegisterForm
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


class PhoneLoginView(LoginView):
    """
    Display the login form and handle the login action.
    """
    form_class = LoginForm
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
    form_class = PasswordResetForm
    template_name = 'phone_auth/password_reset.html'
    success_url = reverse_lazy('phone_auth:phone_password_reset_done')

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PhonePasswordResetDoneView(PasswordResetDoneView):
    template_name = 'phone_auth/password_reset_done.html'


class PhonePasswordConfirmView(PasswordResetConfirmView):
    template_name = 'phone_auth/password_reset_confirm.html'
    success_url = reverse_lazy('phone_auth:phone_password_reset_complete')


class PhonePasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'phone_auth/password_reset_complete.html'
