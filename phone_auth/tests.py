from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from .utils import login_method_allow
from .models import PhoneNumber

User = get_user_model()


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
    def setUpTestData(self):
        user_data = dict(self.data)
        phone = user_data.pop('phone')
        user_data['password'] = make_password(user_data['password'])

        self.user = User.objects.create(**user_data)
        PhoneNumber.objects.create(user=self.user, phone=phone)

    def test_register(self):

        url = reverse('phone_auth:register')
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
        phone = user.phonenumber.phone
        self.assertEqual(
            f'+{phone.country_code}{phone.national_number}',
            data['phone'])
        self.assertTrue(check_password(data['password'], user.password))
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])

    def test_login(self):
        url = reverse('phone_auth:login')
        url_logout = reverse('phone_auth:logout')

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
            response = self.client.get(url_logout)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url,
                settings.LOGOUT_REDIRECT_URL
                if settings.LOGOUT_REDIRECT_URL is not None
                else '/')

            self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        # Login
        url = reverse('phone_auth:login')
        credentials = {
            "login": self.data['phone'],
            "password": self.data["password"]
        }
        response = self.client.post(url, credentials)
        self.assertEqual(response.status_code, 302)

        # Logout
        url = reverse('phone_auth:logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            settings.LOGOUT_REDIRECT_URL
            if settings.LOGOUT_REDIRECT_URL is not None
            else '/')
