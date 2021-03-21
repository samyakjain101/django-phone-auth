# django-phone-auth
A Django app to authenticate and register user using phone/email/username. It uses
default User Model.

## Installation
```
pip install django-phone-auth
```

Add 'phone_auth' in INSTALLED_APPS.

```
INSTALLED_APPS = [
    ...
    'phone_auth'
]
```

Add 'phone_auth.backend.CustomAuthBackend' in AUTHENTICATION_BACKENDS.

```
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    ...
    'phone_auth.backend.CustomAuthBackend',
]
```

Add 'path('accounts/', include('phone_auth.urls'))' in urls.py

```
urlpatterns = [
    ...
    path('accounts/', include('phone_auth.urls'))
]
```

Now run command -

```
python manage.py migrate
```

## Usage

On registration page ('accounts/register/') by default
first_name, last_name, email and username is optional.
These can be set to required by adding following variables
in settings.py

```
REGISTER_USERNAME_REQUIRED = True
REGISTER_EMAIL_REQUIRED = True
REGISTER_FNAME_REQUIRED = True
REGISTER_LNAME_REQUIRED = True

```

On login page ('accounts/login/') by default user can only
login with phone. To allow login through username/email/phone
add following in settings.py
```
LOGIN_METHODS = {'email', 'phone', 'username'}
```

Note: LOGIN_METHODS can't be empty

## Override templates

To override templates, create a folder 'templates' in base directory (directory which contains 'manage.py' file).

Now add path to this folder in settings.py.
It will look like this -

```
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
```

Now in templates folder, you can create file 'register.html', 
'login.html' and templates will get overriden.