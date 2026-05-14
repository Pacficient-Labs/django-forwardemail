API Reference
=============

This section documents the public classes and methods in django-forwardemail.

ForwardEmailService
-------------------

.. autoclass:: django_forwardemail.services.ForwardEmailService
   :members:
   :undoc-members:
   :show-inheritance:

The main service class for sending email through the ForwardEmail API.
``EmailService`` is a backward-compatible alias for ``ForwardEmailService``.

send_email
~~~~~~~~~~

.. automethod:: django_forwardemail.services.ForwardEmailService.send_email
   :no-index:

A keyword-only classmethod that sends a single email through the ForwardEmail
API.

**Parameters:**

* ``to`` (str, required): Recipient email address
* ``subject`` (str, required): Email subject line
* ``text`` (str, required): Plain text email content
* ``from_email`` (str, optional): Sender email address. If omitted, the sender
  is built from the site's ``EmailConfiguration``
* ``html`` (str, optional): HTML email content for rich formatting
* ``reply_to`` (str, optional): Reply-to email address. If omitted, the site's
  configured ``reply_to`` is used
* ``request`` (HttpRequest, optional): Django request object for automatic site
  detection
* ``site`` (Site, optional): Django Site object for explicit site specification
* ``base_url`` (str, optional): Override for the ForwardEmail API base URL

**Returns:** ``dict[str, Any]`` -- the JSON response from the ForwardEmail API.

**Raises:**

* ``django.core.exceptions.ImproperlyConfigured``: when the site cannot be
  determined, or the resolved site has no ``EmailConfiguration``
* ``Exception``: when the API request fails (a non-200 response or a network
  error such as a timeout or connection error)

**Example:**

.. code-block:: python

   from django_forwardemail.services import ForwardEmailService

   ForwardEmailService.send_email(
       to='user@example.com',
       subject='Welcome!',
       text='Welcome to our service',
       html='<h1>Welcome to our service</h1>',
       from_email='noreply@example.com',
       reply_to='support@example.com',
   )

extract_email
~~~~~~~~~~~~~

.. automethod:: django_forwardemail.services.ForwardEmailService.extract_email
   :no-index:

A static method that returns the bare email address from a string. Given
``"Name <email@domain.com>"`` it returns ``"email@domain.com"``; a string that
is already a bare address is returned unchanged (stripped of whitespace).

EmailConfiguration Model
-------------------------

.. autoclass:: django_forwardemail.models.EmailConfiguration
   :members:
   :undoc-members:
   :show-inheritance:

Django model for storing site-specific email configurations. Each Django
``Site`` has exactly one configuration (enforced by
``unique_together = [["site"]]``).

**Fields** (all required except the timestamps):

* ``site`` (ForeignKey to ``django.contrib.sites.models.Site``): the site this
  configuration applies to
* ``api_key`` (CharField, max length 255): ForwardEmail API key
* ``from_email`` (EmailField): default sender email address
* ``from_name`` (CharField, max length 255): default sender display name
* ``reply_to`` (EmailField): default reply-to address
* ``created_at`` (DateTimeField): set automatically on creation
* ``updated_at`` (DateTimeField): set automatically on each save

**Example:**

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.models import EmailConfiguration

   site = Site.objects.get(domain='example.com')
   config = EmailConfiguration.objects.create(
       site=site,
       api_key='your_api_key',
       from_email='noreply@example.com',
       from_name='Example Site',
       reply_to='support@example.com',
   )

ForwardEmailBackend
-------------------

.. autoclass:: django_forwardemail.backends.ForwardEmailBackend
   :members:
   :undoc-members:
   :show-inheritance:

Django email backend that routes Django's standard email helpers through the
ForwardEmail API. It supports ``EmailMessage`` and ``EmailMultiAlternatives``
(HTML + text), extracts the reply-to address from the message, and accepts an
optional ``site`` via the connection or backend kwargs. Because the ForwardEmail
API accepts one recipient per request, the backend sends to the first recipient
of each message.

**send_messages**

.. automethod:: django_forwardemail.backends.ForwardEmailBackend.send_messages
   :no-index:

Sends one or more ``EmailMessage`` instances.

* **Parameters:** ``email_messages`` (sequence of Django ``EmailMessage``
  instances)
* **Returns:** the number of successfully sent messages (int). When
  ``fail_silently`` is true, failures are swallowed and excluded from the count.

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
       ['to@example.com'],
   )

Django Admin Integration
------------------------

.. autoclass:: django_forwardemail.admin.EmailConfigurationAdmin
   :members:
   :undoc-members:
   :show-inheritance:

Django admin interface for managing ``EmailConfiguration`` records. It is
registered automatically when the app is installed.

**Configuration:**

* ``list_display``: ``site``, ``from_name``, ``from_email``, ``reply_to``,
  ``updated_at``
* ``search_fields``: ``site__domain``, ``from_name``, ``from_email``,
  ``reply_to``
* ``list_filter``: ``site``, ``updated_at``, ``created_at``
* ``readonly_fields``: ``created_at``, ``updated_at``
* ``fieldsets``: site, an "Email Settings" group (API key and addresses), and a
  collapsible "Timestamps" group
* The queryset uses ``select_related("site")`` and the site dropdown is ordered
  by domain

App Configuration
-----------------

.. autoclass:: django_forwardemail.apps.DjangoForwardEmailConfig
   :members:
   :undoc-members:
   :show-inheritance:

Django ``AppConfig`` for the package.

**Attributes:**

* ``default_auto_field``: ``"django.db.models.BigAutoField"``
* ``name``: ``"django_forwardemail"``
* ``verbose_name``: ``"Django ForwardEmail"``

Constants and Settings
----------------------

**API base URL**

``ForwardEmailService.DEFAULT_BASE_URL`` is ``"https://api.forwardemail.net"``.
Requests are sent to ``{base_url}/v1/emails``. The base URL can be overridden
per call via the ``base_url`` argument, or globally via the
``FORWARD_EMAIL_BASE_URL`` Django setting.

**Settings**

* ``FORWARD_EMAIL_BASE_URL`` (optional): overrides the ForwardEmail API base URL
* ``EMAIL_BACKEND``: set to ``"django_forwardemail.backends.ForwardEmailBackend"``
  to use ForwardEmail with Django's standard email functions

There are no ``FORWARDEMAIL_*`` settings or environment variables -- API keys
and addresses live in the ``EmailConfiguration`` model.

Errors
------

The package does not define custom exception classes. Callers should handle:

* ``django.core.exceptions.ImproperlyConfigured`` -- raised by
  ``send_email()`` when the site cannot be resolved or has no
  ``EmailConfiguration``
* ``Exception`` -- raised by ``send_email()`` when the ForwardEmail API request
  fails (a non-200 response or a network error)

Migration Support
-----------------

The package ships a single initial migration that creates the
``EmailConfiguration`` table and its foreign key to ``django.contrib.sites``.

.. code-block:: bash

   # Apply migrations
   python manage.py migrate

Testing
-------

``ForwardEmailService.send_email()`` issues a single ``requests.post`` call and
does not go through Django's ``EMAIL_BACKEND``. In tests, patch
``requests.post`` rather than relying on the ``locmem`` backend:

.. code-block:: python

   from unittest.mock import patch
   from django.test import TestCase

   class MyTestCase(TestCase):
       @patch('django_forwardemail.services.requests.post')
       def test_email_sending(self, mock_post):
           mock_post.return_value.status_code = 200
           mock_post.return_value.json.return_value = {}
           # ... call code that sends email ...
           mock_post.assert_called_once()

Version Information
-------------------

.. autodata:: django_forwardemail.__version__

The current package version string.

.. code-block:: python

   import django_forwardemail
   print(django_forwardemail.__version__)

Logging
-------

The package logs through Python's standard ``logging`` module under the
``django_forwardemail`` logger name.

**Log levels used:**

* ``DEBUG``: ForwardEmail API request and response details (only emitted when
  Django ``DEBUG`` is true)
* ``INFO``: general operational messages
* ``ERROR``: failed API requests and service errors

**Example configuration:**

.. code-block:: python

   import logging

   logger = logging.getLogger('django_forwardemail')
   logger.setLevel(logging.INFO)

   handler = logging.StreamHandler()
   handler.setFormatter(
       logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   )
   logger.addHandler(handler)
