Decorators
==========

Verified E-mail Required
------------------------

Even when email verification is not mandatory during signup, there
may be circumstances during which you really want to prevent
unverified users from proceeding. For this purpose you can use the
following decorator::

    from phone_auth.decorators import verified_email_required

    @verified_email_required
    def verified_users_only_view(request):
        ...

The behavior is as follows:

- If the user isn't logged in, it acts identically to the
  ``login_required`` decorator.

- If the user is logged in but has no verified email address,
  then the user gets redirected to the user verification page
  ('/accounts/user_verification/'), where the user can request
  email verification.

Verified Phone Required
------------------------

Work similar to verified_email_required decorator.::

    from phone_auth.decorators import verified_phone_required

    @verified_phone_required
    def verified_users_only_view(request):
        ...
