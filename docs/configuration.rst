Configuration
=============

django-forwardemail provides flexible configuration options for different deployment scenarios and multi-site setups.

EmailConfiguration Model
-------------------------

The package uses a Django model to store site-specific email configurations. Each Django Site can have its own ForwardEmail settings.

Model Fields
~~~~~~~~~~~~

.. code-block:: python

   class EmailConfiguration(models.Model):
       site = models.OneToOneField(Site, on_delete=models.CASCADE)
       api_key = models.CharField(max_length=255)
       from_email = models.EmailField(blank=True, null=True)
       from_name = models.CharField(max_length=255, blank=True, null=True)
       reply_to = models.EmailField(blank=True, null=True)
       created_at = models.DateTimeField(auto_now_add=True)
       updated_at = models.DateTimeField(auto_now=True)

Creating Configurations
~~~~~~~~~~~~~~~~~~~~~~~

You can create email configurations through the Django admin interface or programmatically:

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
       reply_to='support@example.com'
   )

Django Admin Integration
------------------------

The package includes Django admin integration for easy configuration management:

.. code-block:: python

   # In your admin interface, you can:
   # 1. View all email configurations
   # 2. Create new configurations for different sites
   # 3. Edit existing configurations
   # 4. Test email sending directly from admin

The admin interface provides a user-friendly way to manage multiple site configurations without touching code.

Environment-Based Configuration
-------------------------------

For simple single-site deployments, you can use environment variables:

.. code-block:: python

   # settings.py
   import os
   
   # ForwardEmail configuration
   FORWARDEMAIL_API_KEY = os.getenv('FORWARDEMAIL_API_KEY')
   FORWARDEMAIL_FROM_EMAIL = os.getenv('FORWARDEMAIL_FROM_EMAIL', 'noreply@example.com')
   FORWARDEMAIL_FROM_NAME = os.getenv('FORWARDEMAIL_FROM_NAME', 'Your App')
   FORWARDEMAIL_REPLY_TO = os.getenv('FORWARDEMAIL_REPLY_TO')

Site Detection Logic
--------------------

The package uses intelligent site detection to determine which configuration to use:

1. **Explicit Site Parameter**: If a ``site`` parameter is passed to ``send_email()``
2. **Request-Based Detection**: If a ``request`` parameter is provided, extract site from request
3. **Current Site Fallback**: Use Django's ``get_current_site()`` function
4. **Default Site**: Fall back to the default site (ID=1)

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.services import EmailService
   
   # Explicit site specification
   site = Site.objects.get(domain='example.com')
   EmailService.send_email(
       to='user@example.com',
       subject='Welcome!',
       text='Welcome message',
       site=site  # Explicit site
   )
   
   # Request-based detection (in views)
   def my_view(request):
       EmailService.send_email(
           to='user@example.com',
           subject='Welcome!',
           text='Welcome message',
           request=request  # Site extracted from request
       )

Multi-Site Configuration
------------------------

For multi-site Django deployments, create separate configurations for each site:

.. code-block:: python

   from django.contrib.sites.models import Site
   from django_forwardemail.models import EmailConfiguration
   
   # Site 1: Main website
   main_site = Site.objects.create(domain='example.com', name='Main Site')
   EmailConfiguration.objects.create(
       site=main_site,
       api_key='main_site_api_key',
       from_email='noreply@example.com',
       from_name='Example.com'
   )
   
   # Site 2: Blog subdomain
   blog_site = Site.objects.create(domain='blog.example.com', name='Blog')
   EmailConfiguration.objects.create(
       site=blog_site,
       api_key='blog_api_key',
       from_email='blog@example.com',
       from_name='Example Blog'
   )

Configuration Fallbacks
-----------------------

The package implements fallback mechanisms to ensure emails can be sent even with incomplete configuration:

1. **API Key**: Required - will raise error if missing
2. **From Email**: Falls back to Django's ``DEFAULT_FROM_EMAIL`` setting
3. **From Name**: Falls back to site name or empty string
4. **Reply To**: Optional - omitted if not configured

.. code-block:: python

   # Django settings.py fallbacks
   DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
   SERVER_EMAIL = 'server@yourdomain.com'

Security Considerations
-----------------------

API Key Storage
~~~~~~~~~~~~~~~

Never store API keys in version control. Use environment variables or secure configuration management:

.. code-block:: bash

   # Production environment
   export FORWARDEMAIL_API_KEY="your_secure_api_key"
   
   # Development .env file (add to .gitignore)
   FORWARDEMAIL_API_KEY=your_dev_api_key

Key Rotation
~~~~~~~~~~~~

Regularly rotate your ForwardEmail API keys:

1. Generate new API key in ForwardEmail dashboard
2. Update configuration in Django admin or environment variables
3. Test email sending with new key
4. Revoke old API key

Per-Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use different API keys for different environments:

.. code-block:: python

   # settings/production.py
   FORWARDEMAIL_API_KEY = os.getenv('FORWARDEMAIL_PROD_API_KEY')
   
   # settings/staging.py
   FORWARDEMAIL_API_KEY = os.getenv('FORWARDEMAIL_STAGING_API_KEY')
   
   # settings/development.py
   FORWARDEMAIL_API_KEY = os.getenv('FORWARDEMAIL_DEV_API_KEY')

Logging Configuration
---------------------

Configure logging to monitor email sending:

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

For testing environments, you might want to use a test configuration:

.. code-block:: python

   # settings/test.py
   if 'test' in sys.argv:
       # Use a test API key or mock the service
       FORWARDEMAIL_API_KEY = 'test_api_key'
       
       # Or use Django's locmem backend for testing
       EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

Configuration Validation
-------------------------

The package validates configurations before sending emails:

- API key presence and format
- Email address validity
- Site configuration completeness

Invalid configurations will raise descriptive errors to help with debugging.

Best Practices
--------------

1. **Use Environment Variables**: Store sensitive data in environment variables
2. **Separate Environments**: Use different API keys for dev/staging/production
3. **Monitor Logs**: Set up logging to track email sending success/failure
4. **Test Configurations**: Verify email sending works after configuration changes
5. **Backup Configurations**: Export configurations before making changes
6. **Document Settings**: Keep track of which sites use which configurations
