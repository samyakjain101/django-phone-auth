from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    CustomPasswordResetView,
    LoginView,
    RegisterView,
    CustomPasswordResetDoneView
)

app_name = 'phone_auth'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='custom_pass_reset'),
    path('password_reset_done/', CustomPasswordResetDoneView.as_view(), name='custom_pass_reset_done'),
]
