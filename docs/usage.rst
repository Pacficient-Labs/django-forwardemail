Usage
=====

This guide covers the various ways to use django-forwardemail in your Django applications.

Basic Email Sending
--------------------

The simplest way to send emails is using the ``EmailService`` class:

.. code-block:: python

   from django_forwardemail.services import EmailService
   
   # Send a basic email
   EmailService.send_email(
       to='user@example.com',
       subject='Welcome to our service!',
       text='Thank you for signing up. We are excited to have you on board.',
   )

HTML Email Support
------------------

You can send HTML emails by providing both text and HTML content:

.. code-block:: python

   EmailService.send_email(
       to='user@example.com',
       subject='Welcome to our service!',
       text='Thank you for signing up. We are excited to have you on board.',
       html='''
       <html>
           <body>
               <h1>Welcome!</h1>
               <p>Thank you for signing up. We are <strong>excited</strong> to have you on board.</p>
               <p><a href="https://example.com/dashboard">Get Started</a></p>
           </body>
       </html>
       '''
   )

Advanced Parameters
-------------------

The ``send_email`` method supports several optional parameters:

.. code-block:: python

   EmailService.send_email(
       to='user@example.com',
       subject='Custom Email',
       text='Email content',
       html='<p>Email content</p>',
       from_email='custom@example.com',  # Override default from email
       reply_to='support@example.com',   # Set reply-to address
       request=request,                  # For site detection in views
       site=specific_site               # Explicit site specification
   )

Using in Django Views
---------------------

Here are common patterns for using django-forwardemail in Django views:

Registration Confirmation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from django.shortcuts import render, redirect
   from django.contrib.auth import login
   from django.contrib import messages
   from django_forwardemail.services import EmailService
   
   def register_view(request):
       if request.method == 'POST':
           form = UserRegistrationForm(request.POST)
           if form.is_valid():
               user = form.save()
               
               # Send welcome email
               try:
                   EmailService.send_email(
                       to=user.email,
                       subject='Welcome to Example.com!',
                       text=f'Hi {user.first_name}, welcome to our platform!',
                       html=f'<h1>Hi {user.first_name}!</h1><p>Welcome to our platform!</p>',
                       request=request  # Site detection from request
                   )
                   messages.success(request, 'Registration successful! Check your email.')
               except Exception as e:
                   messages.warning(request, 'Registration successful, but email could not be sent.')
               
               login(request, user)
               return redirect('dashboard')
       else:
           form = UserRegistrationForm()
       
       return render(request, 'registration/register.html', {'form': form})

Password Reset
~~~~~~~~~~~~~~

.. code-block:: python

   from django.contrib.auth.tokens import default_token_generator
   from django.utils.http import urlsafe_base64_encode
   from django.utils.encoding import force_bytes
   from django.urls import reverse
   
   def password_reset_view(request):
       if request.method == 'POST':
           email = request.POST.get('email')
           try:
               user = User.objects.get(email=email)
               
               # Generate reset token
               token = default_token_generator.make_token(user)
               uid = urlsafe_base64_encode(force_bytes(user.pk))
               
               # Build reset URL
               reset_url = request.build_absolute_uri(
                   reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
               )
               
               # Send reset email
               EmailService.send_email(
                   to=user.email,
                   subject='Password Reset Request',
                   text=f'Click the link to reset your password: {reset_url}',
                   html=f'''
                   <h2>Password Reset</h2>
                   <p>Click the link below to reset your password:</p>
                   <p><a href="{reset_url}">Reset Password</a></p>
                   <p>If you didn't request this, please ignore this email.</p>
                   ''',
                   request=request
               )
               
               messages.success(request, 'Password reset email sent!')
           except User.DoesNotExist:
               messages.error(request, 'No user found with that email address.')
       
       return render(request, 'registration/password_reset.html')

Using with Django Templates
----------------------------

You can render Django templates for email content:

.. code-block:: python

   from django.template.loader import render_to_string
   from django.utils.html import strip_tags
   
   def send_notification_email(user, notification_data):
       # Render HTML template
       html_content = render_to_string('emails/notification.html', {
           'user': user,
           'notification': notification_data,
           'site_url': 'https://example.com'
       })
       
       # Create plain text version
       text_content = strip_tags(html_content)
       
       EmailService.send_email(
           to=user.email,
           subject=f'New notification: {notification_data.title}',
           text=text_content,
           html=html_content
       )

Template Example
~~~~~~~~~~~~~~~~

.. code-block:: html

   <!-- templates/emails/notification.html -->
   <!DOCTYPE html>
   <html>
   <head>
       <meta charset="utf-8">
       <title>Notification</title>
   </head>
   <body>
       <h1>Hi {{ user.first_name }}!</h1>
       <p>You have a new notification:</p>
       
       <div style="border: 1px solid #ddd; padding: 20px; margin: 20px 0;">
           <h2>{{ notification.title }}</h2>
           <p>{{ notification.message }}</p>
           <p><strong>Date:</strong> {{ notification.created_at|date:"F j, Y" }}</p>
       </div>
       
       <p><a href="{{ site_url }}/notifications/">View all notifications</a></p>
       
       <hr>
       <p><small>This email was sent from {{ site_url }}</small></p>
   </body>
   </html>

Multi-Site Usage
----------------

For multi-site Django deployments, you can specify which site configuration to use:

.. code-block:: python

   from django.contrib.sites.models import Site
   
   def send_site_specific_email(user_email, site_domain):
       # Get specific site
       site = Site.objects.get(domain=site_domain)
       
       EmailService.send_email(
           to=user_email,
           subject=f'Welcome to {site.name}!',
           text=f'Thank you for joining {site.name}.',
           site=site  # Use specific site configuration
       )

Bulk Email Sending
------------------

For sending emails to multiple recipients, send them individually to respect rate limits:

.. code-block:: python

   import time
   from django.contrib.auth.models import User
   
   def send_newsletter(subject, content):
       users = User.objects.filter(is_active=True, email_notifications=True)
       
       for user in users:
           try:
               EmailService.send_email(
                   to=user.email,
                   subject=subject,
                   text=content,
                   html=f'<p>{content}</p>'
               )
               # Small delay to respect rate limits
               time.sleep(0.1)
           except Exception as e:
               print(f"Failed to send email to {user.email}: {e}")

Using as Django Email Backend
-----------------------------

You can configure django-forwardemail as your default Django email backend:

.. code-block:: python

   # settings.py
   EMAIL_BACKEND = 'django_forwardemail.backends.ForwardEmailBackend'

Then use Django's standard email functions:

.. code-block:: python

   from django.core.mail import send_mail, send_mass_mail
   from django.core.mail import EmailMessage, EmailMultiAlternatives
   
   # Using send_mail
   send_mail(
       'Subject',
       'Message body',
       'from@example.com',
       ['to@example.com'],
       fail_silently=False,
   )
   
   # Using EmailMessage for more control
   email = EmailMessage(
       'Subject',
       'Message body',
       'from@example.com',
       ['to@example.com'],
       reply_to=['reply@example.com'],
   )
   email.send()
   
   # Using EmailMultiAlternatives for HTML
   msg = EmailMultiAlternatives(
       'Subject',
       'Text content',
       'from@example.com',
       ['to@example.com']
   )
   msg.attach_alternative('<p>HTML content</p>', "text/html")
   msg.send()

Async Support
-------------

For Django async views, wrap the email sending in ``sync_to_async``:

.. code-block:: python

   from asgiref.sync import sync_to_async
   from django.http import JsonResponse
   
   async def async_send_email_view(request):
       email_data = {
           'to': 'user@example.com',
           'subject': 'Async Email',
           'text': 'This email was sent from an async view',
       }
       
       # Wrap synchronous email sending for async context
       await sync_to_async(EmailService.send_email)(**email_data)
       
       return JsonResponse({'status': 'Email sent successfully'})

Error Handling
--------------

Always handle potential errors when sending emails:

.. code-block:: python

   from django_forwardemail.services import EmailService
   import logging
   
   logger = logging.getLogger(__name__)
   
   def safe_send_email(to, subject, message):
       try:
           EmailService.send_email(
               to=to,
               subject=subject,
               text=message
           )
           logger.info(f"Email sent successfully to {to}")
           return True
       except Exception as e:
           logger.error(f"Failed to send email to {to}: {str(e)}")
           return False

Common Error Types
~~~~~~~~~~~~~~~~~~

- **Configuration Error**: Missing or invalid API key
- **Network Error**: Connection issues with ForwardEmail API
- **Validation Error**: Invalid email addresses
- **Rate Limit Error**: Too many emails sent too quickly
- **Authentication Error**: Invalid API credentials

Testing Email Functionality
----------------------------

For testing, you can use Django's email testing utilities:

.. code-block:: python

   from django.test import TestCase
   from django.core import mail
   from django_forwardemail.services import EmailService
   
   class EmailTestCase(TestCase):
       def test_email_sending(self):
           # Use Django's test email backend
           with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
               EmailService.send_email(
                   to='test@example.com',
                   subject='Test Email',
                   text='Test message'
               )
               
               # Check that email was sent
               self.assertEqual(len(mail.outbox), 1)
               self.assertEqual(mail.outbox[0].to, ['test@example.com'])
               self.assertEqual(mail.outbox[0].subject, 'Test Email')

Best Practices
--------------

1. **Always Handle Errors**: Email sending can fail for various reasons
2. **Use Templates**: Render email content using Django templates
3. **Provide Plain Text**: Always include plain text versions of HTML emails
4. **Respect Rate Limits**: Don't send too many emails too quickly
5. **Log Email Activity**: Keep track of sent emails for debugging
6. **Test Thoroughly**: Test email functionality in different environments
7. **Use Appropriate From Addresses**: Use recognizable from addresses
8. **Include Unsubscribe Links**: For marketing emails, include unsubscribe options
