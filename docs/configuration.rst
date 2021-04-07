Configuration
=============

Available settings:

LOGIN_METHODS (=set)

    Specifies the login method to use – whether the user logs in
    by entering their phone number, username or e-mail address.
    NOTE - ``LOGIN_METHODS`` can't be empty.

    Example::

        # default behaviour - User can only login through phone
        LOGIN_METHODS = {'phone'}

        # User can login through phone or email.
        LOGIN_METHODS = {'phone', 'email'}

        # User can login through phone, email, or username.
        LOGIN_METHODS = {'phone', 'email', 'username'}

        # Works with all possible combinations.

REGISTER_USERNAME_REQUIRED (=False)

    By default, the username field is optional for user registration.
    By changing this setting to ``True``, the username field will be
    set to required.

REGISTER_EMAIL_REQUIRED (=False)

    By default, the email field is optional for user registration.
    By changing this setting to ``True``, the email field will be
    set to required.

REGISTER_FNAME_REQUIRED (=False)

    By default, the first_name field is optional for user registration.
    By changing this setting to ``True``, the first_name field will be
    set to required.

REGISTER_LNAME_REQUIRED (=False)

    By default, the last_name field is optional for user registration.
    By changing this setting to ``True``, the last_name field will be
    set to required.