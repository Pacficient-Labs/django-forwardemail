Installation
============

Requirements
------------

* Django 4.2+ (tested through Django 6.0)
* Python 3.10+
* requests 2.25.0+
* ForwardEmail account and API key

Installing the Package
----------------------

Install django-forwardemail using pip:

.. code-block:: bash

   pip install django-forwardemail

Or using uv (recommended):

.. code-block:: bash

   uv add django-forwardemail

Django Configuration
--------------------

Add ``django.contrib.sites`` and ``django_forwardemail`` to your
``INSTALLED_APPS`` in your Django settings:

.. code-block:: python

   INSTALLED_APPS = [
       # ... other apps
       'django.contrib.sites',  # Required for multi-site support
       'django_forwardemail',
   ]

Optional: Configure as Default Email Backend
--------------------------------------------

You can configure django-forwardemail as your default Django email backend:

.. code-block:: python

   EMAIL_BACKEND = 'django_forwardemail.backends.ForwardEmailBackend'

This allows you to use Django's standard email functions while leveraging ForwardEmail's service.

Database Migration
------------------

Run Django migrations to create the necessary database tables:

.. code-block:: bash

   python manage.py migrate

This will create the ``EmailConfiguration`` model table for storing site-specific email settings.

ForwardEmail Account Setup
--------------------------

1. Sign up for a ForwardEmail account at https://forwardemail.net
2. Generate an API key from your account dashboard
3. Configure your domain and email addresses in ForwardEmail
4. Note your API key for configuration in Django

Create an Email Configuration
-----------------------------

Settings are stored in the ``EmailConfiguration`` model, one per Django
``Site``. Create one through the Django admin (Django ForwardEmail → Email
Configurations) or programmatically:

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.models import EmailConfiguration

   EmailConfiguration.objects.create(
       site=Site.objects.get_current(),
       api_key='your-forwardemail-api-key',
       from_email='noreply@example.com',
       from_name='Example Site',
       reply_to='support@example.com',
   )

See :doc:`configuration` for multi-site setups and details.

Verification
------------

To verify your installation is working correctly, you can test sending an email
once an ``EmailConfiguration`` exists for your site:

.. code-block:: python

   from django_forwardemail.services import ForwardEmailService

   try:
       ForwardEmailService.send_email(
           to='test@example.com',
           subject='Test Email',
           text='This is a test email from django-forwardemail',
       )
       print("Email sent successfully!")
   except Exception as e:
       print(f"Error sending email: {e}")

Next Steps
----------

* Configure your :doc:`configuration` settings
* Learn about :doc:`usage` patterns
