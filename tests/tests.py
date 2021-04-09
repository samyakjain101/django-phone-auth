from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from phone_auth.models import EmailAddress, PhoneNumber
from phone_auth.tokens import phone_token_generator
from phone_auth.utils import login_method_allow


class AccountTests(TestCase):

    data = {
        "phone": "+919876543210",
        "username": "test",
        "email": "someone@example.com",
        "first_name": "first",
        "last_name": "last",
        "password": "abcd@1234"
    }

    @classmethod
    def setUpTestData(cls):
        user_data = dict(cls.data)
        phone = user_data.pop('phone')
        user_data['password'] = make_password(user_data['password'])

        cls.user = User.objects.create(**user_data)
        PhoneNumber.objects.create(user=cls.user, phone=phone)
        EmailAddress.objects.create(user=cls.user, email=user_data['email'])

    def test_phone_register_view(self):

        url = reverse('phone_auth:phone_register')
        data = {
            "phone": "+919999999999",
            "username": "test1",
            "email": "someone@register.com",
            "first_name": "first",
            "last_name": "last",
            "password": "abcd@1234"
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.latest('id')
        phone = user.phonenumber_set.latest('id').phone
        email = user.emailaddress_set.latest('id').email

        self.assertEqual(
            f'+{phone.country_code}{phone.national_number}',
            data['phone'])
        self.assertEqual(email, data['email'])
        self.assertTrue(check_password(data['password'], user.password))
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])

    def test_phone_login_view(self):
        url = reverse('phone_auth:phone_login')

        # With correct password
        for login_method in ['phone', 'email', 'username']:
            # Login
            if not login_method_allow(login_method):
                continue
            credentials = {
                "login": self.data[login_method],
                "password": self.data["password"]
            }
            response = self.client.post(url, credentials)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.wsgi_request.user.is_authenticated)

            # Logout
            self.client.logout()

        # With incorrect password
        for login_method in ['phone', 'email', 'username']:
            if not login_method_allow(login_method):
                continue
            credentials = {
                "login": self.data[login_method],
                "password": 'inco@rrect0Pass'
            }
            response = self.client.post(url, credentials)
            self.assertEqual(response.status_code, 400)
            self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_phone_logout_view(self):
        # Login
        self.client.login(
            login=self.data['email'],
            password=self.data['password'])

        # Logout
        url = reverse('phone_auth:phone_logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            settings.LOGOUT_REDIRECT_URL
            if settings.LOGOUT_REDIRECT_URL is not None
            else '/')

    def test_phone_password_reset_view(self):
        url = reverse('phone_auth:phone_password_reset')

        for method in ['phone', 'email']:
            data = {
                "login": self.data[method]
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 302)

    def test_phone_password_reset_done_view(self):
        url = reverse('phone_auth:phone_password_reset_done')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_phone_password_reset_confirm_view(self):
        # generate `uidb64` and `token`
        credentials = {
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'token': default_token_generator.make_token(self.user)
        }

        url = reverse('phone_auth:phone_password_reset_confirm', kwargs=credentials)
        response = self.client.get(url)
        # print(response)
        self.assertEqual(response.status_code, 302)
        # self.assertEqual(response.url[-14:], '/set-password/')

    def test_phone_password_reset_complete_view(self):
        url = reverse('phone_auth:phone_password_reset_complete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_phone_change_password_view(self):
        url = reverse('phone_auth:phone_change_password')
        data = {
            "old_password": self.data.get('password'),
            "new_password": 'abcd@1234',
            "confirm_password": 'abcd@1234'
        }
        response = self.client.post(url, data)

        user = User.objects.get(email=self.data['email'])
        self.assertEqual(response.status_code, 302)
        self.assertTrue(check_password(data['new_password'], user.password))

    def test_phone_token_generator(self):
        # Test with email
        email_obj = self.user.emailaddress_set.all()[0]
        token_generator = phone_token_generator(
            email_address_obj=email_obj, phone_number_obj=None)
        token = token_generator.make_token(self.user)

        self.assertIsNotNone(token)
        self.assertTrue(token_generator.check_token(self.user, token))

        # Test with phone
        phone_obj = self.user.phonenumber_set.all()[0]
        token_generator = phone_token_generator(
            email_address_obj=None, phone_number_obj=phone_obj)
        token = token_generator.make_token(self.user)

        self.assertIsNotNone(token)
        self.assertTrue(token_generator.check_token(self.user, token))

    def test_phone_email_verification_view(self):
        # Login
        self.client.login(
            login=self.data['email'],
            password=self.data['password'])

        # Test
        url = reverse('phone_auth:phone_email_verification')

        # GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST request (email)
        data = {
            'email': self.data.get('email')
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        # POST request (phone)
        data = {
            'phone': self.data.get('phone')
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
