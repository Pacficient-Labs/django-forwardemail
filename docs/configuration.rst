Configuration
=============

django-forwardemail stores its settings in a Django model so that each site in
a multi-site project can have its own ForwardEmail configuration.

EmailConfiguration Model
-------------------------

The package uses the ``EmailConfiguration`` model to store site-specific email
settings. Each Django ``Site`` has exactly one configuration.

Model Fields
~~~~~~~~~~~~

.. code-block:: python

   class EmailConfiguration(models.Model):
       api_key = models.CharField(max_length=255)
       from_email = models.EmailField()
       from_name = models.CharField(max_length=255)
       reply_to = models.EmailField()
       site = models.ForeignKey(Site, on_delete=models.CASCADE)
       created_at = models.DateTimeField(auto_now_add=True)
       updated_at = models.DateTimeField(auto_now=True)

       class Meta:
           unique_together = [["site"]]  # One configuration per site

All fields except the timestamps are required.

Creating Configurations
~~~~~~~~~~~~~~~~~~~~~~~~~

You can create email configurations through the Django admin interface or
programmatically:

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.models import EmailConfiguration

   # Get or create a site
   site, created = Site.objects.get_or_create(
       domain='example.com',
       defaults={'name': 'Example Site'}
   )

   # Create email configuration
   config = EmailConfiguration.objects.create(
       site=site,
       api_key='your_forwardemail_api_key',
       from_email='noreply@example.com',
       from_name='Example Site',
       reply_to='support@example.com',
   )

Django Admin Integration
------------------------

The package registers ``EmailConfiguration`` with the Django admin so you can
create, view, and edit configurations for each site without touching code. The
admin list view shows the site, from name, from email, and reply-to address,
and supports searching and filtering by site.

Package Settings
----------------

The package itself has only one optional setting. All credentials live in the
``EmailConfiguration`` model rather than in settings or environment variables.

``FORWARD_EMAIL_BASE_URL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Base URL for the ForwardEmail API. Defaults to ``https://api.forwardemail.net``.
You typically only change this for testing or a custom endpoint.

.. code-block:: python

   # settings.py
   FORWARD_EMAIL_BASE_URL = 'https://api.forwardemail.net'

``EMAIL_BACKEND``
~~~~~~~~~~~~~~~~~

Set this to use ForwardEmail with Django's standard email functions:

.. code-block:: python

   # settings.py
   EMAIL_BACKEND = 'django_forwardemail.backends.ForwardEmailBackend'

Site Detection Logic
--------------------

``ForwardEmailService.send_email()`` resolves which configuration to use as
follows:

1. **Explicit Site Parameter**: If a ``site`` argument is passed, it is used.
2. **Request-Based Detection**: If a ``request`` argument is provided,
   ``get_current_site(request)`` is used (it must resolve to a real ``Site``).
3. **Current Site Fallback**: ``Site.objects.get_current()``.
4. **First Site Fallback**: ``Site.objects.first()``.
5. If no site can be determined, ``ImproperlyConfigured`` is raised.

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.services import ForwardEmailService

   # Explicit site specification
   site = Site.objects.get(domain='example.com')
   ForwardEmailService.send_email(
       to='user@example.com',
       subject='Welcome!',
       text='Welcome message',
       site=site,  # Explicit site
   )

   # Request-based detection (in views)
   def my_view(request):
       ForwardEmailService.send_email(
           to='user@example.com',
           subject='Welcome!',
           text='Welcome message',
           request=request,  # Site extracted from request
       )

Multi-Site Configuration
------------------------

For multi-site Django deployments, create separate configurations for each
site:

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.models import EmailConfiguration

   # Site 1: Main website
   main_site = Site.objects.create(domain='example.com', name='Main Site')
   EmailConfiguration.objects.create(
       site=main_site,
       api_key='main_site_api_key',
       from_email='noreply@example.com',
       from_name='Example.com',
       reply_to='support@example.com',
   )

   # Site 2: Blog subdomain
   blog_site = Site.objects.create(domain='blog.example.com', name='Blog')
   EmailConfiguration.objects.create(
       site=blog_site,
       api_key='blog_api_key',
       from_email='blog@example.com',
       from_name='Example Blog',
       reply_to='support@example.com',
   )

How Defaults Are Applied
------------------------

When ``send_email()`` resolves a site, it looks up that site's
``EmailConfiguration`` and applies these rules:

1. **API key**: Always taken from the configuration. If the resolved site has
   no ``EmailConfiguration``, ``ImproperlyConfigured`` is raised.
2. **From email**: If ``from_email`` is not passed, the configured
   ``from_name`` and ``from_email`` are combined into the sender. If
   ``from_email`` is passed without a display name, the configured
   ``from_name`` is added.
3. **Reply-to**: If ``reply_to`` is not passed, the configured ``reply_to`` is
   used.

Security Considerations
-----------------------

API Key Storage
~~~~~~~~~~~~~~~~

API keys are stored in the ``EmailConfiguration`` model. Restrict Django admin
access to trusted staff, and use Django's standard secret-management practices
for your database credentials.

Key Rotation
~~~~~~~~~~~~

Regularly rotate your ForwardEmail API keys:

1. Generate a new API key in the ForwardEmail dashboard
2. Update the ``EmailConfiguration`` (via Django admin or the ORM)
3. Test email sending with the new key
4. Revoke the old API key

Per-Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use different API keys for development, staging, and production by storing the
appropriate key in each environment's database, or by pointing
``FORWARD_EMAIL_BASE_URL`` at a non-production endpoint during testing.

Logging Configuration
---------------------

Configure logging to monitor email sending. The package logs under the
``django_forwardemail`` logger name:

.. code-block:: python

   # settings.py
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
               'style': '{',
           },
       },
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': 'django_forwardemail.log',
               'formatter': 'verbose',
           },
           'console': {
               'level': 'DEBUG',
               'class': 'logging.StreamHandler',
               'formatter': 'verbose',
           },
       },
       'loggers': {
           'django_forwardemail': {
               'handlers': ['file', 'console'],
               'level': 'INFO',
               'propagate': True,
           },
       },
   }

Testing Configuration
---------------------

For tests, mock the ForwardEmail API rather than sending real requests. The
service issues a single ``requests.post`` call, so patching it is sufficient:

.. code-block:: python

   from unittest.mock import patch

   @patch('django_forwardemail.services.requests.post')
   def test_something(mock_post):
       mock_post.return_value.status_code = 200
       mock_post.return_value.json.return_value = {}
       # ... call code that sends email ...

Best Practices
--------------

1. **Restrict admin access**: API keys live in the database and are editable
   through the Django admin.
2. **Separate environments**: Use different API keys for dev/staging/production.
3. **Monitor logs**: Set up logging to track email sending success/failure.
4. **Test configurations**: Verify email sending works after configuration
   changes.
5. **Document settings**: Keep track of which sites use which configurations.
