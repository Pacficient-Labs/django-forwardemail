Installation
============

Requirements
------------

* Django 4.2+
* Python 3.8+
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

Add ``django_forwardemail`` to your ``INSTALLED_APPS`` in your Django settings:

.. code-block:: python

   INSTALLED_APPS = [
       # ... other apps
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

Environment Variables
---------------------

It's recommended to store sensitive configuration in environment variables:

.. code-block:: bash

   # .env file
   FORWARDEMAIL_API_KEY=your_api_key_here
   FORWARDEMAIL_FROM_EMAIL=noreply@yourdomain.com
   FORWARDEMAIL_FROM_NAME="Your App Name"

Then in your Django settings:

.. code-block:: python

   import os
   
   FORWARDEMAIL_API_KEY = os.getenv('FORWARDEMAIL_API_KEY')
   FORWARDEMAIL_FROM_EMAIL = os.getenv('FORWARDEMAIL_FROM_EMAIL')
   FORWARDEMAIL_FROM_NAME = os.getenv('FORWARDEMAIL_FROM_NAME')

Verification
------------

To verify your installation is working correctly, you can test sending an email:

.. code-block:: python

   from django_forwardemail.services import EmailService
   
   try:
       EmailService.send_email(
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
* Set up :doc:`multi-site` support if needed
