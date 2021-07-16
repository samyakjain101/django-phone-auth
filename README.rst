=============================
Welcome to django-phone-auth!
=============================

.. image:: https://github.com/samyakjain101/django-phone-auth/actions/workflows/python-package.yml/badge.svg
 :target: https://github.com/samyakjain101/django-phone-auth/actions/workflows/python-package.yml

.. image:: https://coveralls.io/repos/github/samyakjain101/django-phone-auth/badge.svg?branch=main
 :target: https://coveralls.io/github/samyakjain101/django-phone-auth?branch=main

.. image:: https://app.codacy.com/project/badge/Grade/e4a443a0007e4aa9aeecebb17c4142c0
 :target: https://www.codacy.com/gh/samyakjain101/django-phone-auth/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=samyakjain101/django-phone-auth&amp;utm_campaign=Badge_Grade

.. image:: https://readthedocs.org/projects/django-phone-auth/badge/?version=latest
 :target: https://django-phone-auth.readthedocs.io/en/latest/?badge=latest
 :alt: Documentation Status

.. image:: https://static.pepy.tech/personalized-badge/django-phone-auth?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads
 :target: https://pepy.tech/project/django-phone-auth

A Django library that addresses authentication, registration, and account management using phone-number/email/username.
It uses `django-phonenumber-field[phonenumbers] <https://pypi.org/project/django-phonenumber-field/>`_ to store phone numbers.

Source code
  https://github.com/samyakjain101/django-phone-auth

Documentation
  https://django-phone-auth.readthedocs.io/en/latest/

Features
========

- Login through phone, email, or username.
- User Registration.
- Phone/Email verification.
- Password reset using phone/email.
- Change password.
- Add new email/phone.

Running tests
=============

tox needs to be installed. To run the whole test matrix with the locally
available Python interpreters and generate a combined coverage report::

    tox



.. image:: https://api.codacy.com/project/badge/Grade/113d3c26fd0249cf9c0d6c4b6d7394f7
   :alt: Codacy Badge
   :target: https://app.codacy.com/gh/samyakjain101/django-phone-auth?utm_source=github.com&utm_medium=referral&utm_content=samyakjain101/django-phone-auth&utm_campaign=Badge_Grade_Settings