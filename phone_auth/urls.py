from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (PhoneLoginView, PhonePasswordResetDoneView,
                    PhonePasswordResetView, PhoneRegisterView)

app_name = 'phone_auth'

urlpatterns = [
    path('register/', PhoneRegisterView.as_view(), name='phone_register'),
    path('login/', PhoneLoginView.as_view(), name='phone_login'),
    path('logout/', LogoutView.as_view(), name='phone_logout'),
    path('password_reset/', PhonePasswordResetView.as_view(), name='phone_password_reset'),
    path('password_reset_done/', PhonePasswordResetDoneView.as_view(), name='phone_password_reset_done'),
]
