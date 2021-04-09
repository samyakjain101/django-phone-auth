# from django.contrib.auth.tokens import PasswordResetTokenGenerator
#
#
# class PhoneEmailVerificationTokenGenerator(PasswordResetTokenGenerator):
#
#     def _make_hash_value(self, user, timestamp, phone_number_obj=None, email_address_obj=None):
#
#         if email_address_obj:
#             email = email_address_obj.email
#             is_verified = email_address_obj.is_verified
#             return f'{user.pk}{timestamp}{email}{is_verified}'
#         elif phone_number_obj:
#             pass
#         else:
#             pass
