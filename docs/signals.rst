Signals
=======

There are several signals emitted during authentication flows. You can
hook to them for your own needs.

- ``phone_auth.signals.reset_pass_mail(sender, user, url, email)``
    Sent when someone requests to reset password and email entered
    matches with a user. URL passed in the arguments is relative
    ('/accounts/<uidb64>/<token>/').
    Add domain name as a prefix to the relative URL and send this link to the user
    via email passed in the arguments. Password reset form will appear on opening this link.

- ``phone_auth.signals.reset_pass_phone(sender, user, url, phone)``
    Sent when someone requests to reset password and phone number entered
    matches with a user. URL passed in the arguments is relative
    ('/accounts/<uidb64>/<token>/').
    Add domain name as a prefix to the relative URL and send this link to the user
    via phone number passed in the arguments.
    Password reset form will appear on opening this link.

- ``phone_auth.signals.verify_email(sender, user, url, email)``
    Sent when a user requests to verify email.
    URL passed in the arguments is relative ('/accounts/<uidb64>/<token>/').
    Add domain name as a prefix to the relative URL and send this link to the user
    via email passed in the arguments. The email gets verified on opening this link.

- ``phone_auth.signals.verify_phone(sender, user, url, phone)``
    Sent when a user requests to verify phone.
    URL passed in the arguments is relative ('/accounts/<uidb64>/<token>/').
    Add domain name as a prefix to the relative URL and send this link to the user
    via phone number passed in the arguments.
    The phone gets verified on opening this link.
