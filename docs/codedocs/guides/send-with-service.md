---
title: "Send with the Service Class"
description: "Call ForwardEmailService directly when you need explicit control over site context and payload fields."
---

This guide is for cases where Django's email backend abstraction is not the right fit, such as background jobs, domain services, or code that already thinks in API operations instead of `EmailMessage` objects.

## Problem

You need to send email outside the normal request/response flow or want explicit control over the resolved site, sender overrides, and base URL.

## Solution

Use `django_forwardemail.services.ForwardEmailService.send_email()` directly. It is the canonical send path and accepts raw primitives rather than Django message objects.

<Steps>
<Step>
### Import the service and choose a site strategy

```python
from django.contrib.sites.models import Site
from django_forwardemail.services import ForwardEmailService

site = Site.objects.get(domain="example.com")
```

</Step>
<Step>
### Send a plain-text message

```python
result = ForwardEmailService.send_email(
    to="user@example.com",
    subject="Report ready",
    text="Your export finished successfully.",
    site=site,
)

print(result)
```

</Step>
<Step>
### Add HTML and sender overrides when needed

```python
ForwardEmailService.send_email(
    to="user@example.com",
    subject="Action required",
    text="Open the dashboard to review the change.",
    html="<p>Open the <strong>dashboard</strong> to review the change.</p>",
    from_email="alerts@example.com",
    reply_to="support@example.com",
    site=site,
)
```

</Step>
</Steps>

## Complete Example

```python
from django.contrib.sites.models import Site
from django_forwardemail.services import ForwardEmailService

def send_invoice(site_domain: str, recipient: str, invoice_html: str) -> dict[str, object]:
    site = Site.objects.get(domain=site_domain)

    return ForwardEmailService.send_email(
        to=recipient,
        subject=f"Invoice from {site.domain}",
        text="Your invoice is ready.",
        html=invoice_html,
        site=site,
    )
```

## When to Prefer the Service

- You are running from Celery, cron, management commands, or signal handlers.
- You need to override `base_url` for tests or a non-default ForwardEmail endpoint.
- You already know the target `Site` and want to avoid fallback-based resolution.

## Expected Behavior

The service returns the parsed JSON body from ForwardEmail, so calling code can log or inspect the upstream response directly. It also raises immediately for missing configuration or transport failures, which makes it a better fit than `fail_silently` backends when you want job retries or explicit alerting. Because this is the package's canonical execution path, any behavior change in delivery semantics will show up here first.

Related pages: [Site Resolution](/docs/site-resolution) and [Service API Reference](/docs/api-reference/services).
