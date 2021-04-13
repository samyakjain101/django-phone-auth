Mixins
======

Verified E-mail Required
------------------------

Although email verification is not mandatory during signup, there
may be circumstances during which you really want to prevent
unverified users from proceeding. For this purpose you can use the
following mixin::

    from phone_auth.mixins import VerifiedEmailRequiredMixin

    class VerifiedUsersOnlyView(VerifiedEmailRequiredMixin, View)
        ...

The behavior is as follows:

- If the user isn't logged in, it acts identically to the
  ``LoginRequiredMixin`` decorator.

- If the user is logged in but has no verified email address,
  then the user gets redirected to the user verification page
  ('/accounts/user_verification/'), where the user can request
  email verification.

Verified Phone Required
------------------------

Work similar to VerifiedEmailRequiredMixin.::

    from phone_auth.mixins import VerifiedPhoneRequiredMixin

    class VerifiedUsersOnlyView(VerifiedPhoneRequiredMixin, View)
        ...

