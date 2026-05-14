---
title: "Site Resolution"
description: "See how django-forwardemail determines the active Django Site before loading configuration."
---

Site resolution is the package's routing layer. Without it, `django-forwardemail` could not decide which `EmailConfiguration` record to read in a multi-site deployment.

## What It Is

The relevant public API is the `site` and `request` parameters on:

```python
from django_forwardemail.services import ForwardEmailService

ForwardEmailService.send_email(
    *,
    to: str,
    subject: str,
    text: str,
    from_email: str | None = None,
    html: str | None = None,
    reply_to: str | None = None,
    request: HttpRequest | None = None,
    site: Site | None = None,
    base_url: str | None = None,
) -> dict[str, Any]
```

The logic lives entirely in `django_forwardemail/services.py`. No other module resolves sites independently.

## Why It Exists

Calling code often has different levels of context:

- A Django view has a `request`.
- A Celery task may only know a site ID or domain.
- A simple script may know nothing except that one default site exists.

The service supports each of those contexts without forcing one calling style. That is why site resolution appears before any database lookup or HTTP call inside `send_email()`.

## Resolution Order

```mermaid
flowchart TD
  A[send_email called] --> B{site provided?}
  B -->|Yes| C[Use explicit Site]
  B -->|No| D{request provided?}
  D -->|Yes| E[get_current_site(request)]
  E --> F{real Site instance?}
  F -->|Yes| G[Use request site]
  F -->|No| H[Raise ImproperlyConfigured]
  D -->|No| I[Site.objects.get_current()]
  I --> J{Site exists?}
  J -->|Yes| K[Use current Site]
  J -->|No| L[Site.objects.first()]
  L --> M{Site exists?}
  M -->|Yes| N[Use first Site]
  M -->|No| O[Raise ImproperlyConfigured]
```

The code also makes one specific safety check: when resolving from `request`, it verifies the result is an actual `django.contrib.sites.models.Site`, not a `RequestSite`. If it is not a real database-backed `Site`, the service raises `ImproperlyConfigured("Could not determine site from request")`.

## How It Relates to Other Concepts

- `EmailConfiguration` depends on the resolved `Site`.
- The backend passes `self.site` or `email_message.connection.site` into the service if available.
- Guides for Celery and multi-site deployments usually pass `site` explicitly because workers should not rely on request state.

## How It Works Internally

The service defers all imports related to Django Sites until method execution:

```python
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
```

Those imports happen inside `send_email()` to avoid import-time configuration problems. The method then branches:

1. If `site` is not `None`, it trusts the caller and uses it.
2. Else if `request` is present, it calls `get_current_site(request)` and validates the result.
3. Else it tries `Site.objects.get_current()`.
4. If `get_current()` cannot find a row, it falls back to `Site.objects.first()`.
5. If there is still no site, it raises `ImproperlyConfigured`.

This exact fallback chain is important because the regression test in `tests/test_backend.py` proves the backend must work even when callers do not pass `site` or `request`.

## Basic Usage

In a view, pass `request` and let Django Sites determine the current domain:

```python
from django.http import HttpResponse
from django_forwardemail.services import ForwardEmailService

def contact_submit(request):
    ForwardEmailService.send_email(
        to="support@example.com",
        subject="Contact form",
        text="A user submitted the contact form.",
        request=request,
    )
    return HttpResponse("ok")
```

## Advanced Usage

In background jobs or multi-tenant services, resolve the site explicitly and avoid ambient defaults:

```python
from django.contrib.sites.models import Site
from django_forwardemail.services import ForwardEmailService

def send_tenant_invoice(site_domain: str, recipient: str, body: str) -> None:
    site = Site.objects.get(domain=site_domain)

    ForwardEmailService.send_email(
        to=recipient,
        subject=f"Invoice for {site.domain}",
        text=body,
        site=site,
    )
```

<Callout type="warn">In a true multi-site deployment, relying on `Site.objects.get_current()` or `Site.objects.first()` can silently route email through the wrong site's API key. If the caller already knows the tenant or domain, pass `site` explicitly and treat fallback behavior as a single-site convenience, not a routing strategy.</Callout>

<Accordions>
<Accordion title="Fallback convenience versus explicit correctness">
The fallback chain makes the library easy to adopt because a single-site app can often send mail after creating one `Site` and one `EmailConfiguration`. The cost is ambiguity when multiple `Site` rows exist and the caller omits both `request` and `site`. In that situation the package will still choose a site, but the selection may not match the user's intent. For production multi-tenant systems, explicit `site` values are safer than relying on convenience behavior.
</Accordion>
<Accordion title="Why reject RequestSite values">
`get_current_site(request)` can return a `RequestSite` object when the Sites framework is not configured with a database-backed site. This package rejects that result because the next step is a database query for `EmailConfiguration.objects.get(site=site)`, which only makes sense for real `Site` rows. Accepting `RequestSite` would defer the failure to a less clear error later in the send pipeline. Raising `ImproperlyConfigured` immediately gives you a direct signal that your Sites setup is incomplete.
</Accordion>
</Accordions>

## Debugging Resolution Failures

- If you see `Email configuration is missing for site: ...`, site resolution succeeded but that site has no `EmailConfiguration`.
- If you see `Could not determine site from request`, your request context did not map to a real `Site` row.
- If you see `No sites configured. Please create a Site object.`, the database is missing all `Site` rows.

Next: read [Email Delivery Pipeline](/docs/email-delivery-pipeline) to see how the resolved site turns into an outbound API call.
