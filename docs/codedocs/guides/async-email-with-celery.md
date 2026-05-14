---
title: "Send Email Asynchronously with Celery"
description: "Use ForwardEmailService inside Celery tasks to move delivery out of the request path."
---

This guide shows the safe pattern for background delivery: resolve the site explicitly inside the worker and call the service directly.

## Problem

Sending email in the request path increases latency and couples user-facing responses to an external HTTP API.

## Solution

Queue the send in Celery, pass a stable site identifier into the task payload, and let the worker resolve the `Site` and call `ForwardEmailService.send_email()`.

<Steps>
<Step>
### Define a Celery task that resolves the site explicitly

```python
from celery import shared_task
from django.contrib.sites.models import Site
from django_forwardemail.services import ForwardEmailService

@shared_task
def send_email_async(site_id: int, to: str, subject: str, text: str, html: str | None = None) -> dict[str, object]:
    site = Site.objects.get(id=site_id)
    return ForwardEmailService.send_email(
        to=to,
        subject=subject,
        text=text,
        html=html,
        site=site,
    )
```

</Step>
<Step>
### Queue the task from application code

```python
from django.contrib.sites.shortcuts import get_current_site
from .tasks import send_email_async

def queue_receipt(request, recipient: str) -> None:
    site = get_current_site(request)
    send_email_async.delay(
        site.id,
        recipient,
        "Receipt",
        "Your order has been received.",
        "<p>Your order has been <strong>received</strong>.</p>",
    )
```

</Step>
<Step>
### Handle failures and retries

```python
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_email_with_retry(self, site_id: int, to: str, subject: str, text: str) -> dict[str, object]:
    site = Site.objects.get(id=site_id)
    return ForwardEmailService.send_email(
        to=to,
        subject=subject,
        text=text,
        site=site,
    )
```

</Step>
</Steps>

## Complete Example

```python
def send_welcome_email(user, request) -> None:
    site = get_current_site(request)
    send_email_async.delay(
        site.id,
        user.email,
        "Welcome",
        f"Welcome to {site.name}.",
        f"<h1>Welcome to {site.name}</h1>",
    )
```

## Worker-Side Rules

- Do not pass `request` objects into Celery; pass `site.id` or `site.domain`.
- Do not rely on `Site.objects.first()` in workers when multiple sites exist.
- Keep retries at the task layer because the package itself does not implement retry logic.

Related pages: [Send with the Service Class](/docs/guides/send-with-service) and [Service API Reference](/docs/api-reference/services).
