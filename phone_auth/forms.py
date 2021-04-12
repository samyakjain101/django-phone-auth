import uuid

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db import DatabaseError, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from phonenumber_field.formfields import PhoneNumberField

from phone_auth.validators import validate_username

from . import app_settings
from .models import EmailAddress, PhoneNumber
from .signals import reset_password_email, reset_password_phone

User = get_user_model()


class PhoneRegisterForm(forms.Form):
    """Form for user registration"""

    phone = PhoneNumberField()
    username = forms.CharField(
        required=app_settings.REGISTER_USERNAME_REQUIRED,
        validators=[validate_username])
    email = forms.EmailField(
        required=app_settings.REGISTER_EMAIL_REQUIRED)
    first_name = forms.CharField(
        required=app_settings.REGISTER_FNAME_REQUIRED)
    last_name = forms.CharField(
        required=app_settings.REGISTER_LNAME_REQUIRED)
    password = forms.CharField(widget=forms.PasswordInput())

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password')
        user_data = dict(self.cleaned_data)
        if 'phone' in user_data:
            user_data.pop('phone')
        user_instance = User(**user_data)

        try:
            password_validation.validate_password(
                password, user=user_instance)
        except ValidationError as error:
            self.add_error('password', error)

    def save(self):
        try:
            phone_cleaned = self.cleaned_data.pop('phone')
            if not self.cleaned_data['username']:
                self.cleaned_data['username'] = uuid.uuid4().hex
            self.cleaned_data['password'] = make_password(
                self.cleaned_data['password'])
            email = self.cleaned_data.get('email', None)

            with transaction.atomic():
                user = User.objects.create(**self.cleaned_data)
                PhoneNumber.objects.create(
                    user=user,
                    phone=phone_cleaned)
                if email is not None:
                    EmailAddress.objects.create(
                        user=user,
                        email=email
                    )
        except DatabaseError as e:
            if 'UNIQUE constraint' in e.args[0]:
                if 'phone' in e.args[0]:
                    self.add_error('phone', 'Phone already exists')
                if 'username' in e.args[0]:
                    self.add_error('username', 'Username already exists')
                if 'email' in e.args[0]:
                    self.add_error('email', 'Email already exists')


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
        if PhoneValidationForm({'phone': login}).is_valid():
            lookup_obj |= Q(phonenumber__phone=login)
            is_phone = True

        elif EmailValidationForm({'email': login}).is_valid():
            lookup_obj |= Q(emailaddress__email__iexact=login)

        else:
            return None, False

        try:
            user = User.objects.get(lookup_obj)
            return user, is_phone
        except User.DoesNotExist:
            return None, False

    def save(self):
        login = self.cleaned_data.get('login', None)
        if login is not None:
            user, is_phone = self.get_users_and_method(login)

            if user:
                url = reverse(
                    "phone_auth:phone_password_reset_confirm",
                    kwargs={
                        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user)
                    }
                )
                if is_phone:
                    reset_password_phone.send(sender=self.__class__, user=user, url=url, phone=login)
                else:
                    reset_password_email.send(sender=self.__class__, user=user, url=url, email=login)
