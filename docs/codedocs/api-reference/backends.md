---
title: "ForwardEmailBackend API"
description: "Reference for the Django email backend that adapts EmailMessage objects to ForwardEmailService."
---

Public import path:

```python
from django_forwardemail.backends import ForwardEmailBackend
```

The implementation lives in `django_forwardemail/backends.py`.

## Overview

`ForwardEmailBackend` subclasses Django's `BaseEmailBackend` and provides a drop-in backend for `send_mail()`, `EmailMessage`, and `EmailMultiAlternatives`.

### Class Signature

```python
class ForwardEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently: bool = False, **kwargs)
    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int
```

## Constructor

```python
def __init__(self, fail_silently: bool = False, **kwargs)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fail_silently` | `bool` | `False` | When `True`, send failures are swallowed and omitted from the success count. |
| `site` | `Site \| None` | `None` | Optional keyword-only value in `**kwargs`; stored on `self.site` for later delivery. |
| `**kwargs` | `dict[str, object]` | — | Additional backend kwargs accepted for Django compatibility. |

Usage example:

```python
from django.contrib.sites.models import Site
from django.core.mail import get_connection

connection = get_connection(
    backend="django_forwardemail.backends.ForwardEmailBackend",
    site=Site.objects.get(domain="example.com"),
)
```

## `send_messages`

```python
def send_messages(self, email_messages: Sequence[EmailMessage]) -> int
```

Iterates through the provided messages, calls the internal `_send()` helper on each one, and returns the number of successful sends.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `email_messages` | `Sequence[EmailMessage]` | — | Django message objects to send. |

Returns:

```python
int
```

Usage example:

```python
from django.core.mail import EmailMessage, get_connection

connection = get_connection(backend="django_forwardemail.backends.ForwardEmailBackend")

messages = [
    EmailMessage("One", "Body one", "from@example.com", ["a@example.com"] connection=connection),
    EmailMessage("Two", "Body two", "from@example.com", ["b@example.com"] connection=connection),
]

sent = connection.send_messages(messages)
```

## Internal Helper: `_send`

`_send(self, email_message: EmailMessage) -> bool` is not part of the public API, but understanding it explains the backend's external behavior:

- Returns `False` when `email_message.recipients()` is empty.
- Chooses `email_message.to[0]` as the recipient.
- Uses `email_message.connection.site` when present, else `self.site`.
- Sanitizes `from_email` and strips the display name with `ForwardEmailService.extract_email()`.
- Reads `reply_to` first from `email_message.reply_to`, then from `extra_headers["Reply-To"]`.
- Extracts the first `text/html` alternative from `EmailMultiAlternatives`.

Example with HTML:

```python
from django.core.mail import EmailMultiAlternatives

message = EmailMultiAlternatives(
    subject="Welcome",
    body="Welcome to Example.",
    from_email="noreply@example.com",
    to=["user@example.com"],
)
message.attach_alternative("<h1>Welcome to Example.</h1>", "text/html")
message.send()
```

## Common Patterns

One-recipient fan-out:

```python
def send_to_many(recipients: list[str], subject: str, body: str) -> int:
    total = 0
    for recipient in recipients:
        total += EmailMessage(subject, body, "ops@example.com", [recipient]).send()
    return total
```

Related pages: [Use the Django Email Backend](/docs/guides/use-django-email-backend) and [Email Delivery Pipeline](/docs/email-delivery-pipeline).
