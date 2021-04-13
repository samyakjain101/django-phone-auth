from django.urls import path

from .views import (
    PhoneChangePasswordDoneView,
    PhoneChangePasswordView,
    PhoneEmailVerificationConfirmView,
    PhoneEmailVerificationView,
    PhoneLoginView,
    PhoneLogoutView,
    PhonePasswordConfirmView,
    PhonePasswordResetCompleteView,
    PhonePasswordResetDoneView,
    PhonePasswordResetView,
    PhoneRegisterView,
)

app_name = "phone_auth"

urlpatterns = [
    path("register/", PhoneRegisterView.as_view(), name="phone_register"),
    path("login/", PhoneLoginView.as_view(), name="phone_login"),
    path("logout/", PhoneLogoutView.as_view(), name="phone_logout"),
    path(
        "password_reset/", PhonePasswordResetView.as_view(), name="phone_password_reset"
    ),
    path(
        "password_reset_done/",
        PhonePasswordResetDoneView.as_view(),
        name="phone_password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        PhonePasswordConfirmView.as_view(),
        name="phone_password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        PhonePasswordResetCompleteView.as_view(),
        name="phone_password_reset_complete",
    ),
    path(
        "change_password/",
        PhoneChangePasswordView.as_view(),
        name="phone_change_password",
    ),
    path(
        "change_password_done/",
        PhoneChangePasswordDoneView.as_view(),
        name="phone_change_password_done",
    ),
    path(
        "user_verification/",
        PhoneEmailVerificationView.as_view(),
        name="phone_email_verification",
    ),
    path(
        "user_verification_confirm/<idb64>/<token>/",
        PhoneEmailVerificationConfirmView.as_view(),
        name="phone_email_verification_confirm",
    ),
]
