import string

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import View

from phone_auth import app_settings
from phone_auth.app_settings import AuthenticationMethod
from phone_auth.decorators import (
    anonymous_required,
    verified_email_required,
    verified_phone_required,
)
from phone_auth.mixins import (
    AnonymousRequiredMixin,
    VerifiedEmailRequiredMixin,
    VerifiedPhoneRequiredMixin,
)
from phone_auth.models import EmailAddress, PhoneNumber
from phone_auth.tokens import phone_token_generator
from phone_auth.validators import validate_username


class AccountTests(TestCase):
    data = {
        "phone": "+919876543210",
        "username": "test",
        "email": "someone@example.com",
        "first_name": "first",
        "last_name": "last",
        "password": "abcd@1234",
    }

    @classmethod
    def setUpTestData(cls):
        user_data = dict(cls.data)
        phone = user_data.pop("phone")
        user_data["password"] = make_password(user_data["password"])

        cls.user = User.objects.create(**user_data)
        cls.phone_obj = PhoneNumber.objects.create(user=cls.user, phone=phone)
        cls.email_obj = EmailAddress.objects.create(
            user=cls.user, email=user_data["email"]
        )

    def test_phone_signup_view(self):

        url = reverse("phone_auth:phone_signup")
        data = {
            "phone": "+919999999999",
            "username": "test1",
            "email": "someone@register.com",
            "first_name": "first",
            "last_name": "last",
            "password": "abcd@1234",
            "confirm_password": "abcd@1234",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.latest("id")
        phone = user.phonenumber_set.latest("id").phone
        email = user.emailaddress_set.latest("id").email

        self.assertEqual(phone.__str__(), data["phone"])
        self.assertEqual(email, data["email"])
        self.assertTrue(check_password(data["password"], user.password))
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])

    def test_phone_login_view(self):
        url = reverse("phone_auth:phone_login")
        authentication_methods = app_settings.AUTHENTICATION_METHODS

        # With correct password
        for auth_method in authentication_methods:
            credentials = {
                "login": self.data[auth_method],
                "password": self.data["password"],
            }
            response = self.client.post(url, credentials)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.wsgi_request.user.is_authenticated)

            # Logout
            self.client.logout()

        # With incorrect password
        for auth_method in authentication_methods:
            credentials = {
                "login": self.data[auth_method],
                "password": "inco@rrect0Pass",
            }
            response = self.client.post(url, credentials)
            self.assertEqual(response.status_code, 400)
            self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_phone_logout_view(self):
        # Login
        self.client.login(login=self.data["email"], password=self.data["password"])

        # Logout
        url = reverse("phone_auth:phone_logout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_phone_password_reset_view(self):
        url = reverse("phone_auth:phone_password_reset")

        for method in ["phone", "email"]:
            data = {"login": self.data[method]}
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 302)

    def test_phone_password_reset_done_view(self):
        url = reverse("phone_auth:phone_password_reset_done")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_phone_password_reset_confirm_view(self):
        # generate `uidb64` and `token`
        credentials = {
            "uidb64": urlsafe_base64_encode(force_bytes(self.user.pk)),
            "token": default_token_generator.make_token(self.user),
        }

        url = reverse("phone_auth:phone_password_reset_confirm", kwargs=credentials)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # self.assertEqual(response.url[-14:], '/set-password/')

    def test_phone_password_reset_complete_view(self):
        url = reverse("phone_auth:phone_password_reset_complete")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_phone_change_password_view(self):
        url = reverse("phone_auth:phone_change_password")
        data = {
            "old_password": self.data.get("password"),
            "new_password": "abcd@1234",
            "confirm_password": "abcd@1234",
        }
        response = self.client.post(url, data)

        user = User.objects.get(email=self.data["email"])
        self.assertEqual(response.status_code, 302)
        self.assertTrue(check_password(data["new_password"], user.password))

    def test_phone_token_generator(self):
        # Test with email
        email_obj = self.user.emailaddress_set.all()[0]
        token_generator = phone_token_generator(
            email_address_obj=email_obj, phone_number_obj=None
        )
        token = token_generator.make_token(self.user)

        self.assertIsNotNone(token)
        self.assertTrue(token_generator.check_token(self.user, token))

        # Test with phone
        phone_obj = self.user.phonenumber_set.all()[0]
        token_generator = phone_token_generator(
            email_address_obj=None, phone_number_obj=phone_obj
        )
        token = token_generator.make_token(self.user)

        self.assertIsNotNone(token)
        self.assertTrue(token_generator.check_token(self.user, token))

    def test_phone_email_verification_view(self):
        # Login
        self.client.login(login=self.data["email"], password=self.data["password"])

        # Test
        url = reverse("phone_auth:phone_email_verification")

        # GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST request (email)
        data = {"method": "email", "pk": self.email_obj.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        # POST request (phone)
        data = {"method": "phone", "pk": self.phone_obj.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_phone_email_verification_confirm_view(self):
        # Email verification
        self.assertFalse(self.email_obj.is_verified)
        credentials = {
            "idb64": urlsafe_base64_encode(force_bytes(f"email{self.email_obj.pk}")),
            "token": phone_token_generator(
                email_address_obj=self.email_obj, phone_number_obj=None
            ).make_token(self.user),
        }
        url = reverse("phone_auth:phone_email_verification_confirm", kwargs=credentials)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EmailAddress.objects.get(pk=self.email_obj.pk).is_verified)

        # Phone Verification
        self.assertFalse(self.phone_obj.is_verified)
        credentials = {
            "idb64": urlsafe_base64_encode(force_bytes(f"phone{self.phone_obj.pk}")),
            "token": phone_token_generator(
                email_address_obj=None, phone_number_obj=self.phone_obj
            ).make_token(self.user),
        }
        url = reverse("phone_auth:phone_email_verification_confirm", kwargs=credentials)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PhoneNumber.objects.get(pk=self.phone_obj.pk).is_verified)

    def test_anonymous_required_decorator(self):
        @anonymous_required
        def tview(request):
            return HttpResponse()

        request = self.client.get("/").wsgi_request
        self.assertTrue(request.user.is_anonymous)
        response = tview(request)
        self.assertEqual(response.status_code, 200)

        # checking for logged in user
        self.client.login(login=self.data["email"], password=self.data["password"])
        request = self.client.get("/").wsgi_request
        self.assertTrue(request.user.is_authenticated)
        response = tview(request)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url, f"{app_settings.LOGIN_REDIRECT_URL}?{REDIRECT_FIELD_NAME}=/"
        )

    def test_verified_email_required_decorator(self):

        if AuthenticationMethod.EMAIL in app_settings.AUTHENTICATION_METHODS:

            @verified_email_required
            def tview(request):
                return HttpResponse()

            self.client.login(login=self.data["email"], password=self.data["password"])
            request = self.client.get("/").wsgi_request

            # check with not verified email
            response = tview(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url, reverse("phone_auth:phone_email_verification")
            )

            # check with verified email
            self.email_obj.is_verified = True
            self.email_obj.save()
            response = tview(request)
            self.assertEqual(response.status_code, 200)

    def test_verified_phone_required_decorator(self):

        if AuthenticationMethod.PHONE in app_settings.AUTHENTICATION_METHODS:

            @verified_phone_required
            def tview(request):
                return HttpResponse()

            self.client.login(login=self.data["phone"], password=self.data["password"])
            request = self.client.get("/").wsgi_request

            # check with not verified phone
            response = tview(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url, reverse("phone_auth:phone_email_verification")
            )

            # check with verified email
            self.phone_obj.is_verified = True
            self.phone_obj.save()
            response = tview(request)
            self.assertEqual(response.status_code, 200)

    def test_anonymous_required_mixin(self):
        class Tview(AnonymousRequiredMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse()

        request = self.client.get("/").wsgi_request
        response = Tview.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # checking for logged in user
        self.client.login(login=self.data["email"], password=self.data["password"])
        request = self.client.get("/").wsgi_request
        response = Tview.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, app_settings.LOGIN_REDIRECT_URL)

    def test_verified_phone_required_mixin(self):

        if AuthenticationMethod.PHONE in app_settings.AUTHENTICATION_METHODS:

            class Tview(VerifiedPhoneRequiredMixin, View):
                def get(self, request, *args, **kwargs):
                    return HttpResponse()

            self.client.login(login=self.data["phone"], password=self.data["password"])

            request = self.client.get("/").wsgi_request

            # check with not verified phone
            response = Tview.as_view()(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url, reverse("phone_auth:phone_email_verification")
            )

            # check with verified phone
            self.phone_obj.is_verified = True
            self.phone_obj.save()
            response = Tview.as_view()(request)
            self.assertEqual(response.status_code, 200)

    def test_verified_email_required_mixin(self):

        if AuthenticationMethod.EMAIL in app_settings.AUTHENTICATION_METHODS:

            class Tview(VerifiedEmailRequiredMixin, View):
                def get(self, request, *args, **kwargs):
                    return HttpResponse()

            self.client.login(login=self.data["email"], password=self.data["password"])
            request = self.client.get("/").wsgi_request

            # check with not verified email
            response = Tview.as_view()(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url, reverse("phone_auth:phone_email_verification")
            )

            # check with verified email
            self.email_obj.is_verified = True
            self.email_obj.save()
            response = Tview.as_view()(request)
            self.assertEqual(response.status_code, 200)

    def test_username_validator(self):
        self.assertIsNone(validate_username("a"))
        self.assertIsNone(validate_username("A"))
        self.assertIsNone(validate_username("a" * 150))
        self.assertIsNone(validate_username(string.digits))
        self.assertIsNone(validate_username(string.ascii_lowercase))
        self.assertIsNone(validate_username(string.ascii_uppercase))
        self.assertIsNone(validate_username("."))
        self.assertIsNone(validate_username("-"))
        self.assertIsNone(validate_username("_"))
        try:
            self.assertIsNone(validate_username(""))
            # If exception not raised, test case failed.
            self.assertTrue(False)
        except ValidationError:
            pass
        try:
            self.assertIsNone(validate_username("+"))
            self.assertTrue(False)
        except ValidationError:
            pass
        try:
            self.assertIsNone(validate_username("@"))
            self.assertTrue(False)
        except ValidationError:
            pass

    def test_add_email_view(self):
        # Login
        self.client.login(login=self.data["email"], password=self.data["password"])

        url = reverse("phone_auth:add_email")

        # test with different mail should pass
        data = {"email": "someone1@register.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(EmailAddress.objects.filter(email=data["email"]).exists())

    def test_add_phone_view(self):
        # Login
        self.client.login(login=self.data["phone"], password=self.data["password"])

        url = reverse("phone_auth:add_phone")

        # test with different phone no should pass
        data = {"phone": "+919876543211"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(PhoneNumber.objects.filter(phone=data["phone"]).exists())
