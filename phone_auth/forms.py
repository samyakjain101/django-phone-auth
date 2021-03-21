import uuid
from django import forms
from django.db import DatabaseError, transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from phone_auth.utils import get_setting, validate_username
from phonenumber_field.formfields import PhoneNumberField
from .models import PhoneNumber

User = get_user_model()


class RegisterForm(forms.Form):
    phone = PhoneNumberField()
    username = forms.CharField(
        required=get_setting('REGISTER_USERNAME_REQUIRED', default=False),
        validators=[validate_username])
    email = forms.EmailField(
        required=get_setting('REGISTER_EMAIL_REQUIRED', default=False))
    first_name = forms.CharField(
        required=get_setting('REGISTER_FNAME_REQUIRED', default=False))
    last_name = forms.CharField(
        required=get_setting('REGISTER_LNAME_REQUIRED', default=False))
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
            with transaction.atomic():
                phone_cleaned = self.cleaned_data.pop('phone')
                if not self.cleaned_data['username']:
                    self.cleaned_data['username'] = uuid.uuid4().hex
                self.cleaned_data['password'] = make_password(
                    self.cleaned_data['password'])

                user = User.objects.create(**self.cleaned_data)
                PhoneNumber.objects.create(
                    user=user,
                    phone=phone_cleaned)
        except DatabaseError as e:
            if 'UNIQUE constraint' in e.args[0]:
                if 'phone' in e.args[0]:
                    self.add_error('phone', 'Phone already exists')
                if 'username' in e.args[0]:
                    self.add_error('username', 'Username already exists')
                if 'email' in e.args[0]:
                    self.add_error('email', 'Email already exists')

        return user


class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class EmailValidationForm(forms.Form):
    email = forms.EmailField()


class PhoneValidationForm(forms.Form):
    phone = PhoneNumberField()


class UsernameValidationForm(forms.Form):
    username = forms.CharField(validators=[validate_username])
