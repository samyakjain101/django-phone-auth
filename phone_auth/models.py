from django.contrib.auth import get_user_model
from django.db import models

# noinspection PyUnresolvedReferences
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class PhoneNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(unique=True, blank=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.phone)


class EmailAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True, blank=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email
