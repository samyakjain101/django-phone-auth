from django.contrib import admin

from .models import EmailAddress, PhoneNumber


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)


@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
