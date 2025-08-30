API Reference
=============

This section provides detailed documentation for all classes, methods, and functions in django-forwardemail.

EmailService Class
------------------

.. autoclass:: django_forwardemail.services.EmailService
   :members:
   :undoc-members:
   :show-inheritance:

The main service class for sending emails through ForwardEmail.

send_email Method
~~~~~~~~~~~~~~~~~

.. automethod:: django_forwardemail.services.EmailService.send_email

**Parameters:**

* ``to`` (str, required): Recipient email address
* ``subject`` (str, required): Email subject line
* ``text`` (str, required): Plain text email content
* ``from_email`` (str, optional): Sender email address. If not provided, uses configuration default or Django's ``DEFAULT_FROM_EMAIL``
* ``html`` (str, optional): HTML email content for rich formatting
* ``reply_to`` (str, optional): Reply-to email address
* ``request`` (HttpRequest, optional): Django request object for automatic site detection
* ``site`` (Site, optional): Django Site object for explicit site specification

**Returns:** None

**Raises:**

* ``EmailConfigurationError``: When email configuration is missing or invalid
* ``ForwardEmailAPIError``: When the ForwardEmail API request fails
* ``ValidationError``: When email addresses are invalid or malformed

**Example:**

.. code-block:: python

   from django_forwardemail.services import EmailService
   
   EmailService.send_email(
       to='user@example.com',
       subject='Welcome!',
       text='Welcome to our service',
       html='<h1>Welcome to our service</h1>',
       from_email='noreply@example.com',
       reply_to='support@example.com'
   )

EmailConfiguration Model
-------------------------

.. autoclass:: django_forwardemail.models.EmailConfiguration
   :members:
   :undoc-members:
   :show-inheritance:

Django model for storing site-specific email configurations.

**Fields:**

* ``site`` (OneToOneField): Reference to Django Site model
* ``api_key`` (CharField): ForwardEmail API key (max 255 characters)
* ``from_email`` (EmailField): Default sender email address (optional)
* ``from_name`` (CharField): Default sender name (optional, max 255 characters)
* ``reply_to`` (EmailField): Default reply-to address (optional)
* ``created_at`` (DateTimeField): Timestamp when configuration was created
* ``updated_at`` (DateTimeField): Timestamp when configuration was last modified

**Methods:**

.. automethod:: django_forwardemail.models.EmailConfiguration.__str__

Returns a string representation of the configuration.

**Example:**

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.models import EmailConfiguration
   
   site = Site.objects.get(domain='example.com')
   config = EmailConfiguration.objects.create(
       site=site,
       api_key='your_api_key',
       from_email='noreply@example.com',
       from_name='Example Site'
   )

ForwardEmailBackend Class
-------------------------

.. autoclass:: django_forwardemail.backends.ForwardEmailBackend
   :members:
   :undoc-members:
   :show-inheritance:

Django email backend implementation for seamless integration with Django's email system.

**Methods:**

.. automethod:: django_forwardemail.backends.ForwardEmailBackend.send_messages

Sends one or more EmailMessage instances.

**Parameters:**

* ``email_messages`` (list): List of Django EmailMessage instances

**Returns:** Number of successfully sent messages (int)

**Example:**

.. code-block:: python

   # settings.py
   EMAIL_BACKEND = 'django_forwardemail.backends.ForwardEmailBackend'
   
   # Usage with Django's email functions
   from django.core.mail import send_mail
   
   send_mail(
       'Subject',
       'Message',
       'from@example.com',
       ['to@example.com']
   )

Django Admin Integration
------------------------

.. autoclass:: django_forwardemail.admin.EmailConfigurationAdmin
   :members:
   :undoc-members:
   :show-inheritance:

Django admin interface for managing email configurations.

**Features:**

* List view with site, API key (masked), and email addresses
* Search functionality by site domain and email addresses
* Filtering by site and creation date
* Inline editing capabilities
* Bulk actions for common operations

**Admin Configuration:**

.. code-block:: python

   # Automatically registered when app is installed
   # Provides interface for:
   # - Creating new email configurations
   # - Editing existing configurations
   # - Viewing configuration history
   # - Testing email sending

App Configuration
-----------------

.. autoclass:: django_forwardemail.apps.DjangoForwardemailConfig
   :members:
   :undoc-members:
   :show-inheritance:

Django app configuration class.

**Attributes:**

* ``default_auto_field``: Specifies the default primary key field type
* ``name``: App name for Django's app registry
* ``verbose_name``: Human-readable app name for admin interface

Constants and Settings
----------------------

**API Endpoint:**

.. code-block:: python

   FORWARDEMAIL_API_URL = 'https://api.forwardemail.net/v1/emails'

**Default Configuration Keys:**

.. code-block:: python

   # Environment variable names
   FORWARDEMAIL_API_KEY = 'FORWARDEMAIL_API_KEY'
   FORWARDEMAIL_FROM_EMAIL = 'FORWARDEMAIL_FROM_EMAIL'
   FORWARDEMAIL_FROM_NAME = 'FORWARDEMAIL_FROM_NAME'
   FORWARDEMAIL_REPLY_TO = 'FORWARDEMAIL_REPLY_TO'

Exception Classes
-----------------

EmailConfigurationError
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: django_forwardemail.exceptions.EmailConfigurationError

Raised when email configuration is missing or invalid.

**Common Causes:**

* Missing API key
* Invalid site configuration
* Malformed configuration data

**Example:**

.. code-block:: python

   try:
       EmailService.send_email(to='user@example.com', subject='Test', text='Test')
   except EmailConfigurationError as e:
       print(f"Configuration error: {e}")

ForwardEmailAPIError
~~~~~~~~~~~~~~~~~~~~

.. autoexception:: django_forwardemail.exceptions.ForwardEmailAPIError

Raised when ForwardEmail API requests fail.

**Common Causes:**

* Network connectivity issues
* Invalid API credentials
* Rate limiting
* Server errors

**Example:**

.. code-block:: python

   try:
       EmailService.send_email(to='user@example.com', subject='Test', text='Test')
   except ForwardEmailAPIError as e:
       print(f"API error: {e}")

ValidationError
~~~~~~~~~~~~~~~

.. autoexception:: django_forwardemail.exceptions.ValidationError

Raised when email data validation fails.

**Common Causes:**

* Invalid email address format
* Missing required fields
* Data type mismatches

**Example:**

.. code-block:: python

   try:
       EmailService.send_email(to='invalid-email', subject='Test', text='Test')
   except ValidationError as e:
       print(f"Validation error: {e}")

Utility Functions
-----------------

Site Detection
~~~~~~~~~~~~~~

.. autofunction:: django_forwardemail.utils.get_site_from_request

Extracts Django Site from request object.

**Parameters:**

* ``request`` (HttpRequest): Django request object

**Returns:** Site object or None

**Example:**

.. code-block:: python

   from django_forwardemail.utils import get_site_from_request
   
   def my_view(request):
       site = get_site_from_request(request)
       if site:
           print(f"Current site: {site.domain}")

Configuration Retrieval
~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: django_forwardemail.utils.get_email_configuration

Retrieves email configuration for a given site.

**Parameters:**

* ``site`` (Site, optional): Django Site object
* ``request`` (HttpRequest, optional): Django request object

**Returns:** EmailConfiguration object or None

**Example:**

.. code-block:: python

   from django_forwardemail.utils import get_email_configuration
   
   config = get_email_configuration(site=my_site)
   if config:
       print(f"API key configured: {bool(config.api_key)}")

Email Validation
~~~~~~~~~~~~~~~~

.. autofunction:: django_forwardemail.utils.validate_email_address

Validates email address format.

**Parameters:**

* ``email`` (str): Email address to validate

**Returns:** bool - True if valid, False otherwise

**Example:**

.. code-block:: python

   from django_forwardemail.utils import validate_email_address
   
   if validate_email_address('user@example.com'):
       print("Valid email address")

Migration Support
-----------------

The package includes Django migrations for database schema management:

**Initial Migration (0001_initial.py):**

* Creates EmailConfiguration model table
* Sets up foreign key relationship with Django Sites
* Creates appropriate indexes for performance

**Migration Commands:**

.. code-block:: bash

   # Apply migrations
   python manage.py migrate django_forwardemail
   
   # Create new migration (if you modify models)
   python manage.py makemigrations django_forwardemail

Testing Utilities
-----------------

Mock Email Service
~~~~~~~~~~~~~~~~~~

For testing purposes, you can mock the EmailService:

.. code-block:: python

   from unittest.mock import patch
   from django.test import TestCase
   
   class MyTestCase(TestCase):
       @patch('django_forwardemail.services.EmailService.send_email')
       def test_email_sending(self, mock_send_email):
           # Your test code here
           mock_send_email.assert_called_once()

Test Email Backend
~~~~~~~~~~~~~~~~~~

Use Django's test email backend for testing:

.. code-block:: python

   # settings/test.py
   EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

Version Information
-------------------

.. autodata:: django_forwardemail.__version__

Current package version string.

**Example:**

.. code-block:: python

   import django_forwardemail
   print(f"Package version: {django_forwardemail.__version__}")

Logging
-------

The package uses Python's standard logging module with the logger name ``django_forwardemail``.

**Log Levels:**

* ``DEBUG``: Detailed API request/response information
* ``INFO``: Successful operations and configuration changes
* ``WARNING``: Recoverable errors and fallback usage
* ``ERROR``: Failed operations and configuration errors
* ``CRITICAL``: System-level failures

**Example Configuration:**

.. code-block:: python

   import logging
   
   # Get package logger
   logger = logging.getLogger('django_forwardemail')
   logger.setLevel(logging.INFO)
   
   # Add handler
   handler = logging.StreamHandler()
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   handler.setFormatter(formatter)
   logger.addHandler(handler)
