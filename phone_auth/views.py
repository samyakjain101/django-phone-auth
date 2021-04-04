from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView

from .forms import LoginForm, RegisterForm


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = '/'

    def form_valid(self, form):
        form.save()
        if form.errors:
            return render(
                self.request, 'register.html', context={'form': form})
        return super().form_valid(form)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = '/'

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
