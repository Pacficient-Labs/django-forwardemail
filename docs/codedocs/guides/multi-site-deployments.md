---
title: "Configure Multi-Site Deployments"
description: "Set up separate ForwardEmail credentials and sender identities for each Django Site."
---

This guide covers the package's primary use case: multiple domains, one Django codebase, and isolated sender settings per site.

## Problem

A single Django deployment serves more than one domain, and each domain needs its own ForwardEmail API key, `from` identity, and `reply_to` address.

## Solution

Create one `Site` row and one `EmailConfiguration` row per domain, then pass `request` or `site` at send time so the service chooses the correct configuration.

<Steps>
<Step>
### Create one Site per domain

```python
from django.contrib.sites.models import Site

main_site, _ = Site.objects.get_or_create(
    domain="example.com",
    defaults={"name": "Example"},
)

blog_site, _ = Site.objects.get_or_create(
    domain="blog.example.com",
    defaults={"name": "Example Blog"},
)
```

</Step>
<Step>
### Create matching EmailConfiguration rows

```python
from django_forwardemail.models import EmailConfiguration

EmailConfiguration.objects.update_or_create(
    site=main_site,
    defaults={
        "api_key": "fe_live_main",
        "from_email": "noreply@example.com",
        "from_name": "Example",
        "reply_to": "support@example.com",
    },
)

EmailConfiguration.objects.update_or_create(
    site=blog_site,
    defaults={
        "api_key": "fe_live_blog",
        "from_email": "newsletter@blog.example.com",
        "from_name": "Example Blog",
        "reply_to": "editors@blog.example.com",
    },
)
```

</Step>
<Step>
### Pass site context deliberately

```python
from django_forwardemail.services import ForwardEmailService

ForwardEmailService.send_email(
    to="reader@example.com",
    subject="New article",
    text="A new article is live on the blog.",
    site=blog_site,
)
```

</Step>
</Steps>

## Complete Example

```python
from django.contrib.sites.shortcuts import get_current_site
from django_forwardemail.services import ForwardEmailService

def send_contact_confirmation(request, recipient: str) -> None:
    site = get_current_site(request)
    ForwardEmailService.send_email(
        to=recipient,
        subject=f"Thanks for contacting {site.name}",
        text="We received your message and will reply shortly.",
        request=request,
    )
```

## Deployment Pattern

- Use `request=request` inside views when the incoming host is authoritative.
- Use `site=...` in jobs, scripts, and webhook handlers.
- Treat `Site.objects.first()` fallback as a bootstrap helper, not a tenant router.

## Operational Checklist

- Verify every production domain has a matching `Site` row.
- Verify every active `Site` row has exactly one `EmailConfiguration`.
- Rotate API keys per site instead of sharing one credential across all domains.
- Test each tenant path with a real send after changing `from_email`, `from_name`, or `reply_to`.

Related pages: [Email Configuration](/docs/email-configuration) and [Site Resolution](/docs/site-resolution).
