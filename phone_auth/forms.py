import uuid

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# noinspection PyUnresolvedReferences
from phonenumber_field.formfields import PhoneNumberField

from phone_auth.validators import validate_username

from . import app_settings
from .models import EmailAddress, PhoneNumber
from .signals import (
    reset_password_email,
    reset_password_phone,
    verify_email,
    verify_phone,
)
from .tokens import phone_token_generator

User = get_user_model()


class PhoneRegisterForm(forms.Form):
    """Form for user registration"""

    phone = PhoneNumberField()
    username = forms.CharField(
        required=app_settings.REGISTER_USERNAME_REQUIRED, validators=[validate_username]
    )
    email = forms.EmailField(required=app_settings.REGISTER_EMAIL_REQUIRED)
    first_name = forms.CharField(required=app_settings.REGISTER_FNAME_REQUIRED)
    last_name = forms.CharField(required=app_settings.REGISTER_LNAME_REQUIRED)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=app_settings.REGISTER_CONFIRM_PASSWORD_REQUIRED,
    )

    def clean(self):
        errors = {}
        if app_settings.REGISTER_CONFIRM_PASSWORD_REQUIRED:
            if self.cleaned_data.get("password") != self.cleaned_data.get(
                "confirm_password"
            ):
                errors["confirm_password"] = "Password didn't match"
        if self.cleaned_data.get("email", None) is not None:
            if EmailAddress.objects.filter(
                email__iexact=self.cleaned_data.get("email")
            ).exists():
                errors["email"] = "Email already exists"
        if self.cleaned_data.get("phone", None) is not None:
            if PhoneNumber.objects.filter(
                phone=self.cleaned_data.get("phone")
            ).exists():
                errors["phone"] = "Phone already exists"
        if self.cleaned_data.get("username", None) is not None:
            if User.objects.filter(
                username__exact=self.cleaned_data.get("username")
            ).exists():
                errors["username"] = "Username already exists"

        if errors:
            raise ValidationError(errors)

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password")
        user_data = dict(self.cleaned_data)
        if "phone" in user_data:
            user_data.pop("phone")
        if "confirm_password" in user_data:
            user_data.pop("confirm_password")
        user_instance = User(**user_data)

        try:
            password_validation.validate_password(password, user=user_instance)
        except ValidationError as error:
            self.add_error("password", error)

    def save(self):
        try:
            phone = self.cleaned_data.get("phone", None)
            if phone is not None:
                self.cleaned_data.pop("phone")

            if "confirm_password" in self.cleaned_data:
                self.cleaned_data.pop("confirm_password")

            username = self.cleaned_data.get("username")
            if not username:
                self.cleaned_data["username"] = uuid.uuid4().hex

            email = self.cleaned_data.get("email", None)

            self.cleaned_data["password"] = make_password(self.cleaned_data["password"])

            with transaction.atomic():
                user = User.objects.create(**self.cleaned_data)
                if phone is not None:
                    PhoneNumber.objects.create(user=user, phone=phone)
                if email is not None:
                    EmailAddress.objects.create(user=user, email=email)
        except DatabaseError as e:
            if "UNIQUE constraint" in e.args[0]:
                if "phone" in e.args[0]:
                    self.add_error("phone", "Phone already exists")
                if "username" in e.args[0]:
                    self.add_error("username", "Username already exists")
                if "email" in e.args[0]:
                    self.add_error("email", "Email already exists")


class PhoneLoginForm(forms.Form):
    """Form used for user login"""

    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(PhoneLoginForm, self).__init__(*args, **kwargs)


class EmailValidationForm(forms.Form):
    """Form to validate email field"""

    email = forms.EmailField()


class PhoneValidationForm(forms.Form):
    """Form to validate phone field"""

    phone = PhoneNumberField()


class UsernameValidationForm(forms.Form):
    """Form to validate username field"""

    username = forms.CharField(validators=[validate_username])


class PhonePasswordResetForm(forms.Form):
    """Checks if the user with provided email/phone exists.

    If provided email/phone exists, send reset_password_email/reset_password_phone
    signal with user and URL (relative_path that is one-time use only link
    to reset password) arguments.
    """

    login = forms.CharField()

    @staticmethod
    def get_users_and_method(login):
        lookup_obj = Q()

        is_phone = False
        if PhoneValidationForm({"phone": login}).is_valid():
            lookup_obj |= Q(phonenumber__phone=login)
            is_phone = True

        elif EmailValidationForm({"email": login}).is_valid():
            lookup_obj |= Q(emailaddress__email__iexact=login)

        else:
            return None, False

        try:
            user = User.objects.get(lookup_obj)
            return user, is_phone
        except User.DoesNotExist:
            return None, False

    def save(self):
        login = self.cleaned_data.get("login", None)
        if login is not None:
            user, is_phone = self.get_users_and_method(login)

            if user:
                url = reverse(
                    "phone_auth:phone_password_reset_confirm",
                    kwargs={
                        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    },
                )
                if is_phone:
                    reset_password_phone.send(
                        sender=self.__class__, user=user, url=url, phone=login
                    )
                else:
                    reset_password_email.send(
                        sender=self.__class__, user=user, url=url, email=login
                    )


class PhoneEmailVerificationForm(forms.Form):
    """
    Send verify_email/verify_phone signal with user instance
    and relative_url which is one-time use link to verify email/phone
    user requested to verify.
    """

    method = forms.CharField(max_length=5)
    pk = forms.IntegerField()

    def save(self, user):
        method = self.cleaned_data.get("method")
        pk = self.cleaned_data.get("pk")
        if method == "email":
            try:
                email_obj = EmailAddress.objects.get(user=user, pk=pk)
                if email_obj.is_verified:
                    return "Email already Verified"

                url = self._get_token_url(
                    email_obj=email_obj, phone_obj=None, user=user
                )
                verify_email.send(
                    sender=self.__class__,
                    user=user,
                    url=url,
                    email=email_obj.email,
                )
                return "Email Verification Sent"
            except EmailAddress.DoesNotExist:
                # In this case say email sent successfully
                # to avoid user enumeration attack
                pass
        elif method == "phone":
            try:
                phone_obj = PhoneNumber.objects.get(user=user, pk=pk)
                if phone_obj.is_verified:
                    return "Phone already Verified"

                url = self._get_token_url(
                    email_obj=None, phone_obj=phone_obj, user=user
                )
                verify_phone.send(
                    sender=self.__class__,
                    user=user,
                    url=url,
                    phone=phone_obj.phone.__str__(),
                )
                return "Phone Verification Sent"
            except PhoneNumber.DoesNotExist:
                pass

        return "Something Went Wrong"

    def _get_token_url(self, email_obj, phone_obj, user):
        token = phone_token_generator(
            email_address_obj=email_obj, phone_number_obj=phone_obj
        ).make_token(user)
        url = reverse(
            "phone_auth:phone_email_verification_confirm",
            kwargs={
                "idb64": self._get_email_phone_b64(email_obj, phone_obj),
                "token": token,
            },
        )
        return url

    @staticmethod
    def _get_email_phone_b64(email_obj, phone_obj):
        if email_obj is not None:
            return urlsafe_base64_encode(force_bytes(f"email{email_obj.pk}"))
        if phone_obj is not None:
            return urlsafe_base64_encode(force_bytes(f"phone{phone_obj.pk}"))


class PhoneLogoutForm(forms.Form):
    pass


class AddPhoneForm(forms.Form):
    """Form to add new phone number"""

    phone = PhoneNumberField(required=True)

    def save(self, user):
        try:
            phone = self.cleaned_data.get("phone")
            PhoneNumber.objects.create(user=user, phone=phone)

        except IntegrityError as e:
            if "UNIQUE constraint" in e.args[0]:
                self.add_error("phone", "Phone already exists")


class AddEmailForm(forms.Form):
    """Form to add new email"""

    email = forms.EmailField(required=True)

    def save(self, user):
        try:
            email = self.cleaned_data.get("email")
            EmailAddress.objects.create(user=user, email=email)

        except IntegrityError as e:
            if "UNIQUE constraint" in e.args[0]:
                self.add_error("email", "Email already exists")
