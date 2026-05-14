---
title: "Use the Django Email Backend"
description: "Configure django-forwardemail as Django's default backend and send mail through standard Django helpers."
---

This guide shows the most common integration path: keep using Django's built-in email APIs, but route delivery through ForwardEmail.

## Problem

Your code already uses `send_mail()`, `EmailMessage`, or `EmailMultiAlternatives`, and you want those calls to deliver through ForwardEmail without rewriting every call site.

## Solution

Set `EMAIL_BACKEND` to `django_forwardemail.backends.ForwardEmailBackend`, create one `EmailConfiguration` for the active site, and then keep using Django's normal email APIs.

<Steps>
<Step>
### Configure Django settings

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django_forwardemail",
]

SITE_ID = 1
EMAIL_BACKEND = "django_forwardemail.backends.ForwardEmailBackend"
FORWARD_EMAIL_BASE_URL = "https://api.forwardemail.net"
```

</Step>
<Step>
### Run migrations and create the configuration row

```bash
python manage.py migrate
python manage.py shell
```

```python
from django.contrib.sites.models import Site
from django_forwardemail.models import EmailConfiguration

EmailConfiguration.objects.update_or_create(
    site=Site.objects.get_current(),
    defaults={
        "api_key": "fe_live_site_1",
        "from_email": "noreply@example.com",
        "from_name": "Example App",
        "reply_to": "support@example.com",
    },
)
```

</Step>
<Step>
### Send plain-text and HTML messages

```python
from django.core.mail import send_mail, EmailMultiAlternatives

send_mail(
    subject="Plain text alert",
    message="The import finished successfully.",
    from_email="noreply@example.com",
    recipient_list=["user@example.com"],
    fail_silently=False,
)

message = EmailMultiAlternatives(
    subject="Welcome",
    body="Welcome to Example.",
    from_email="noreply@example.com",
    to=["user@example.com"],
)
message.attach_alternative("<h1>Welcome to Example.</h1>", "text/html")
message.send()
```

</Step>
</Steps>

## Complete Example

```python
from django.core.mail import send_mail

def notify_user(email: str) -> None:
    send_mail(
        subject="Account ready",
        message="Your account has been provisioned.",
        from_email="noreply@example.com",
        recipient_list=[email],
        fail_silently=False,
    )
```

## Notes

- The backend sends one recipient per `EmailMessage`, using only `message.to[0]`.
- If you pass a message-level `reply_to`, the backend forwards that value to the service.
- If `fail_silently=False`, missing site config or HTTP errors bubble up as exceptions.
- This approach is best when most of your code already uses Django mail helpers and you want the smallest migration surface.

## Expected Behavior

When the configuration exists and the API call succeeds, Django's helpers behave the same way they normally do with any backend:

- `send_mail(...)` returns `1` for one successfully sent message.
- `EmailMessage.send()` returns `1` when the backend reports success.
- `EmailMultiAlternatives` forwards the plain-text body plus the first `text/html` alternative to the service.

Related pages: [Email Delivery Pipeline](/docs/email-delivery-pipeline) and [Backend API Reference](/docs/api-reference/backends).
