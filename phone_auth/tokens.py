from django.contrib.auth.tokens import PasswordResetTokenGenerator


class PhoneEmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Generate/Verify one-time use token for email/phone verification"""

    def __init__(self, email_address_obj, phone_number_obj):
        super(PhoneEmailVerificationTokenGenerator, self).__init__()

        if email_address_obj is None and phone_number_obj is None:
            raise TypeError(
                "Both email_address_obj and" " phone_number_obj arguments can't be None"
            )

        self.email_address_obj = email_address_obj
        self.phone_number_obj = phone_number_obj

    def _make_hash_value(self, user, timestamp):

        if self.email_address_obj:
            email = self.email_address_obj.email
            is_verified = self.email_address_obj.is_verified
            return f"{user.pk}{timestamp}{email}{is_verified}"

        elif self.phone_number_obj:
            phone = self.phone_number_obj.phone
            country_code = phone.country_code
            national_number = phone.national_number
            is_verified = self.phone_number_obj.is_verified
            return f"{user.pk}{timestamp}{country_code}{national_number}{is_verified}"


phone_token_generator = PhoneEmailVerificationTokenGenerator
