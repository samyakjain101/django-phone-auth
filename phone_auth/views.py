from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import (PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView

from .forms import LoginForm, PasswordResetForm, RegisterForm


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'phone_auth/register.html'
    success_url = '/'

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        if form.errors:
            return render(
                self.request, 'register.html', context={'form': form})
        return super().form_valid(form)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'phone_auth/login.html'
    success_url = '/'

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(
                settings.LOGIN_REDIRECT_URL
                if settings.LOGIN_REDIRECT_URL is not None
                else '/')
        return super(LoginView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = authenticate(self.request, **form.cleaned_data)
        if user is not None:
            login(self.request, user)
        else:
            form.add_error('login', 'Invalid Credentials')
            return render(
                self.request, 'login.html', context={'form': form}, status=400)
        return super().form_valid(form)


class CustomPasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = 'phone_auth/password_reset.html'
    success_url = reverse_lazy('phone_auth:custom_pass_reset_done')

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'phone_auth/password_reset_done.html'


class CustomPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'phone_auth/password_reset_confirm.html'
    success_url = reverse_lazy('phone_auth:custom_pass_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'phone_auth/password_reset_complete.html'
