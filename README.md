# django-phone-auth
A Django app to authenticate and register users using phone/email/username. It uses the default User Model.

## Installation
```
pip install django-phone-auth
```

Add 'phone_auth' in INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ...
    'phone_auth',
    ...
]
```

Add 'phone_auth.backend.CustomAuthBackend' in AUTHENTICATION_BACKENDS.

```python
AUTHENTICATION_BACKENDS = [
    ...
    # Needed to login by username in Django admin, regardless of `django-phone-auth`
    'django.contrib.auth.backends.ModelBackend',
    
    # `django-phone-auth` specific authentication methods, such as login by phone/email/username.
    'phone_auth.backend.CustomAuthBackend',
    ...
]
```

Add 'path('accounts/', include('phone_auth.urls'))' in urls.py

```python
urlpatterns = [
    ...
    path('accounts/', include('phone_auth.urls')),
    ...
]
```

Now run command -

```
python manage.py migrate
```

## Usage

On registration page ('/accounts/register/') by default
first_name, last_name, email and username is optional.
These can be set to required by adding following variables
in settings.py

```python
REGISTER_USERNAME_REQUIRED = True
REGISTER_EMAIL_REQUIRED = True
REGISTER_FNAME_REQUIRED = True
REGISTER_LNAME_REQUIRED = True

```

On login page ('/accounts/login/') by default user can only
login with phone. To allow login through username/email/phone
add the following in settings.py
```python
LOGIN_METHODS = {'email', 'phone', 'username'}
```

Note: LOGIN_METHODS can't be empty

## Override templates

To override templates, create a folder 'templates' in the base directory (the directory which contains the 'manage.py' file).
Now add the path to this folder in settings.py. It will look like this -

```python
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

Now in templates folder, you can create file 'register.html', 'login.html' and templates will get overriden.