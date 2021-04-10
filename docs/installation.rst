Installation
============

Python package::

    pip install django-phone-auth

settings.py::

    AUTHENTICATION_BACKENDS = [
        ...
        # Needed to login by username in Django admin, regardless of `django-phone-auth`
        'django.contrib.auth.backends.ModelBackend',

        # `django-phone-auth` specific authentication methods, such as login by phone/email/username.
        'phone_auth.backend.CustomAuthBackend',
        ...
    ]

    INSTALLED_APPS = [
        ...
        'phone_auth',
        ...
    ]

urls.py::

    urlpatterns = [
        ...
        path('accounts/', include('phone_auth.urls')),
        ...
    ]

Post-Installation
-----------------

In your Django root execute the command below to create your database tables::

    python manage.py migrate
