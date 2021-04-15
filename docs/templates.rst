Templates
=========

Overridable templates
---------------------

``django-phone-auth`` ships many templates, viewable in the
`phone_auth/templates <https://github.com/samyakjain101/django-phone-auth/tree/main/phone_auth/templates>`__
directory.

For instance, the view corresponding to the ``login`` URL uses the
template ``phone_auth/login.html``. If you create a file with this name in your
code layout, it can override the one shipped with ``django-phone-auth``.

To override templates, create a folder 'templates' in the base directory
(the directory which contains the 'manage.py' file).

settings.py::

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
