---
title: "Getting Started"
description: "Set up django-forwardemail, connect it to Django Sites, and send your first email through the ForwardEmail API."
---

`django-forwardemail` connects Django's email APIs and the Django Sites framework to the ForwardEmail HTTP API so each site can send mail with its own credentials and sender defaults.

## The Problem

- Django's built-in email backends expect SMTP-style delivery, while ForwardEmail exposes an HTTP API.
- Multi-site Django projects often need different API keys, sender identities, and reply-to addresses per domain.
- Application code should not need to know how to build auth headers, choose the current `Site`, or normalize sender fields.
- Teams still want to keep using familiar Django primitives such as `send_mail()` and `EmailMultiAlternatives`.

## The Solution

`django-forwardemail` stores one `EmailConfiguration` per Django `Site`, resolves the active site at send time, and routes either direct service calls or Django email backend calls through `ForwardEmailService.send_email()` in `django_forwardemail/services.py`.

```python
from django.contrib.sites.models import Site
from django_forwardemail.models import EmailConfiguration
from django_forwardemail.services import ForwardEmailService

site = Site.objects.get_current()

EmailConfiguration.objects.get_or_create(
    site=site,
    defaults={
        "api_key": "fe_live_xxx",
        "from_email": "noreply@example.com",
        "from_name": "Example App",
        "reply_to": "support@example.com",
    },
)

response = ForwardEmailService.send_email(
    to="user@example.com",
    subject="Welcome",
    text="Your account is ready.",
    site=site,
)

print(response)
```

## Installation

<Tabs items={["pip", "uv", "poetry", "pipenv"]}>
<Tab value="pip">

```bash
pip install django-forwardemail
```

</Tab>
<Tab value="uv">

```bash
uv add django-forwardemail
```

</Tab>
<Tab value="poetry">

```bash
poetry add django-forwardemail
```

</Tab>
<Tab value="pipenv">

```bash
pipenv install django-forwardemail
```

</Tab>
</Tabs>

Add the app to Django and optionally make it the default backend:

```python
INSTALLED_APPS = [
    "django.contrib.sites",
    "django_forwardemail",
]

SITE_ID = 1
EMAIL_BACKEND = "django_forwardemail.backends.ForwardEmailBackend"
FORWARD_EMAIL_BASE_URL = "https://api.forwardemail.net"
```

Run migrations:

```bash
python manage.py migrate
```

## Quick Start

The minimum working setup is one `Site`, one matching `EmailConfiguration`, and one send call. The package reads the configuration from the database, not from environment variables.

```python
from django.contrib.sites.models import Site
from django_forwardemail.models import EmailConfiguration
from django_forwardemail.services import ForwardEmailService

site = Site.objects.get_current()

EmailConfiguration.objects.update_or_create(
    site=site,
    defaults={
        "api_key": "fe_test_123",
        "from_email": "hello@example.com",
        "from_name": "Example",
        "reply_to": "support@example.com",
    },
)

result = ForwardEmailService.send_email(
    to="recipient@example.com",
    subject="Test Email",
    text="This is a test email from django-forwardemail.",
)

print(result)
```

Expected output:

```python
{"queued": True}
```

That response shape comes directly from the mocked API contract in `tests/test_backend.py`, where successful sends return a JSON object and the backend reports `1` sent message when the HTTP call succeeds.

## Key Features

- One `EmailConfiguration` record per Django `Site`, enforced by a database uniqueness constraint.
- Drop-in Django backend at `django_forwardemail.backends.ForwardEmailBackend`.
- Direct service layer at `django_forwardemail.services.ForwardEmailService`.
- Automatic site detection from `request`, explicit `site`, `Site.objects.get_current()`, or the first stored `Site`.
- Plain-text and HTML email support, including `EmailMultiAlternatives`.
- Debug logging around outbound requests and responses when `DEBUG=True`.

<Cards>
  <Card title="Architecture" href="/docs/architecture">Trace how the model, service, and backend work together.</Card>
  <Card title="Core Concepts" href="/docs/email-configuration">Learn the main abstractions behind configuration, site resolution, and delivery.</Card>
  <Card title="API Reference" href="/docs/api-reference/services">Inspect signatures, parameters, and source-backed behavior for every public module.</Card>
</Cards>
