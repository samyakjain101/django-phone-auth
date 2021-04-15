.. _signals:

Signals
=======

There are several signals emitted during authentication flows. You can
hook to them for your own needs.

.. _reset-password-email-signal:

phone_auth.signals.reset_password_email(sender, user, url, email)
-----------------------------------------------------------------

- Sent when someone requests to reset password.
- ``url`` passed in the arguments is relative ('/accounts/password_reset_confirm/<uidb64>/<token>/').
- Add domain name as a prefix to the ``url`` and send this link to the user
  via ``email`` passed in the arguments.
- Password reset form will appear on opening this link.

Example::

    from django.dispatch import receiver
    from phone_auth.signals import reset_password_email

    @receiver(reset_password_email)
    def reset_password_email_signal(sender, user, url, email, **kwargs):
        ...
        # Send email
        ...

.. _reset-password-phone-signal:

phone_auth.signals.reset_password_phone(sender, user, url, phone)
-----------------------------------------------------------------

- Sent when someone requests to reset password.
- ``url`` passed in the arguments is relative ('/accounts/password_reset_confirm/<uidb64>/<token>/').
- Add domain name as a prefix to the ``url`` and send this link to the user
  via ``phone`` passed in the arguments.
- Password reset form will appear on opening this link.

Example::

    from django.dispatch import receiver
    from phone_auth.signals import reset_password_phone

    @receiver(reset_password_phone)
    def reset_password_phone_signal(sender, user, url, phone, **kwargs):
        ...
        # Send SMS
        ...

.. _verify-email-signal:

phone_auth.signals.verify_email(sender, user, url, email)
---------------------------------------------------------

- Sent when a user requests to verify email.
- URL passed in the arguments is relative ('/accounts/user_verification_confirm/<idb64>/<token>/').
- Add domain name as a prefix to the ``url`` and send this link to the user
  via ``email`` passed in the arguments.
- The email gets verified on opening this link.

Example::

    from django.dispatch import receiver
    from phone_auth.signals import verify_email

    @receiver(verify_email)
    def verify_email_signal(sender, user, url, email, **kwargs):
        ...
        # Send email
        ...

.. _verify-phone-signal:

phone_auth.signals.verify_phone(sender, user, url, phone)
---------------------------------------------------------
- Sent when a user requests to verify phone.
- URL passed in the arguments is relative ('/accounts/user_verification_confirm/<idb64>/<token>/').
- Add domain name as a prefix to the ``url`` and send this link to the user
  via ``phone`` passed in the arguments.
- The phone gets verified on opening this link.

Example::

    from django.dispatch import receiver
    from phone_auth.signals import verify_phone

    @receiver(verify_phone)
    def verify_phone_signal(sender, user, url, phone, **kwargs):
        ...
        # Send SMS
        ...
