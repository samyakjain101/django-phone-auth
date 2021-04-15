Views
=====

Login (``phone_login``)
-------------------------

Users login via the ``phone_auth.views.PhoneLoginView`` view over at
``/accounts/login/`` (URL name ``phone_login``).

Signup (``phone_signup``)
---------------------------

Users sign up via the ``phone_auth.views.PhoneSignupView`` view over at
``/accounts/signup/`` (URL name ``phone_signup``).


Logout (``phone_logout``)
----------------------------

The logout view (``phone_auth.views.PhoneLogoutView``) over at
``/accounts/logout/`` (URL name ``phone_logout``) requests for confirmation
before logging out. The user is logged out only when the confirmation is
received by means of a POST request.

If you are wondering why, consider what happens when a malicious user
embeds the following image in a post::

    <img src="http://example.com/accounts/logout/">

For this and more background information on the subject, see:

- https://code.djangoproject.com/ticket/15619
- http://stackoverflow.com/questions/3521290/logout-get-or-post

If you insist on having logout on GET, then please consider adding a
bit of Javascript to automatically turn a click on a logout link into
a POST.


Change Password (``phone_change_password``)
-------------------------------------------

Authenticated users can change their password using
(``phone_auth.views.PhoneChangePasswordView``) view over at
``/accounts/change_password/`` (URL name ``phone_change_password``).


Password Reset (``phone_password_reset``)
-------------------------------------------

Users can request a password reset using the
``phone_auth.views.PhonePasswordResetView`` view over at
``/accounts/password_reset/`` (URL name ``phone_password_reset``).
A signal :ref:`reset_password_email <reset-password-email-signal>`/:ref:`reset_password_phone <reset-password-phone-signal>` will be sent with
reset link (relative URL), user instance and email/phone.
See :ref:`signals` for the details.


Phone/E-mail Verification
-------------------------

Users can request a phone/email verification using the
``phone_auth.views.PhoneEmailVerificationView`` view over at
``/accounts/user_verification/`` (URL name ``phone_email_verification``).
A signal :ref:`verify_email <verify-email-signal>`/:ref:`verify_phone <verify-phone-signal>` will be sent with
verification link (relative URL), user instance and email/phone.
See :ref:`signals` for the details.


Add New Phone/Email
-------------------
Users can add phone/email using
``phone_auth.views.AddPhoneView`` / ``phone_auth.views.AddEmailView`` view over at
``/accounts/phone/add/`` / ``/accounts/email/add/`` (URL name ``add_phone`` / ``add_email``).