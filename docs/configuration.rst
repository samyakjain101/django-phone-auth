Configuration
=============

Available settings:

AUTHENTICATION_METHODS (={'phone', 'email', 'username'})
    Specifies the login method to use – whether the user logs in
    by entering their phone number, username or e-mail address.
    NOTE - ``AUTHENTICATION_METHODS`` can't be empty.

    Example::

        # default behaviour - User can login through phone, email, or username.
        AUTHENTICATION_METHODS = {'phone', 'email', 'username'}

        # User can login through phone or email.
        AUTHENTICATION_METHODS = {'phone', 'email'}

        # User can only login through phone.
        AUTHENTICATION_METHODS = {'phone'}

        # Works with all possible combinations.

REGISTER_USERNAME_REQUIRED (=True)
    By default, the username field is required for user registration.
    By changing this setting to ``False``, the username field will be
    set to optional.

REGISTER_EMAIL_REQUIRED (=True)
    By default, the email field is required for user registration.
    By changing this setting to ``False``, the email field will be
    set to optional.

REGISTER_FNAME_REQUIRED (=True)
    By default, the first_name field is required for user registration.
    By changing this setting to ``False``, the first_name field will be
    set to optional.

REGISTER_LNAME_REQUIRED (=True)
    By default, the last_name field is required for user registration.
    By changing this setting to ``False``, the last_name field will be
    set to optional.

REGISTER_CONFIRM_PASSWORD_REQUIRED (=True)
    By default, the confirm_password field is required for user registration.
    By changing this setting to ``False``, the confirm_password field will be
    set to optional.

LOGIN_REDIRECT_URL (='/accounts/profile/')
    Specifies which URL to redirect after successful login.
    By default, it is '/accounts/profile/'.

LOGOUT_REDIRECT_URL (='/')
    Specifies which URL to redirect after successful logout.
    By default, it is '/'.
