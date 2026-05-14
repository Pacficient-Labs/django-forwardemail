---
title: "Email Configuration"
description: "Learn how django-forwardemail stores sender defaults and API credentials per Django site."
---

`EmailConfiguration` is the package's core persistence concept. It exists so the rest of the system can be stateless at send time: once the active `Site` is known, the service can look up one row and derive every required sender value.

## What It Is

The public import path is:

```python
from django_forwardemail.models import EmailConfiguration
```

The model is defined in `django_forwardemail/models.py` and created by the migration in `django_forwardemail/migrations/0001_initial.py`.

```python
class EmailConfiguration(models.Model):
    api_key = models.CharField(max_length=255)
    from_email = models.EmailField()
    from_name = models.CharField(max_length=255)
    reply_to = models.EmailField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

The `Meta.unique_together = [["site"]]` constraint makes the relationship one-to-one in practice even though the database field is a `ForeignKey`. That matters because `ForwardEmailService.send_email()` assumes exactly one configuration row for the resolved site when it calls `EmailConfiguration.objects.get(site=site)`.

## Why It Exists

The package is built for multi-site Django deployments, where one codebase may serve several domains. Keeping the API key and sender defaults in the database solves two concrete problems:

- Each `Site` can have its own ForwardEmail credentials.
- Operations teams can change sender details in Django admin without redeploying code.
- Application code does not need to pass `api_key`, `from_name`, or `reply_to` on every send.

## How It Relates to Other Concepts

- `ForwardEmailService` uses `EmailConfiguration` to populate the `Authorization` header and default sender fields.
- `ForwardEmailBackend` depends on the service, so it also depends indirectly on `EmailConfiguration`.
- `EmailConfigurationAdmin` is the editing surface for the model inside Django admin.
- Site resolution decides *which* `EmailConfiguration` row gets used.

## How It Works Internally

The model itself is simple, but the important behavior emerges from how the service reads it:

1. `ForwardEmailService.send_email()` resolves a `Site`.
2. The service loads `email_config = EmailConfiguration.objects.get(site=site)`.
3. `api_key` is read from the model and encoded into Basic auth.
4. `from_email` is built from `from_name` and `from_email` unless you override it in the method call.
5. `reply_to` falls back to the stored `reply_to` unless you override it.

Because `reply_to` and `from_email` are model fields instead of optional settings, a valid row always contains a complete sender identity. This is why the package can expose a minimal `send_email()` signature without forcing callers to pass everything explicitly.

```mermaid
flowchart TD
  A[Resolved Site] --> B[EmailConfiguration.objects.get(site=site)]
  B --> C[api_key]
  B --> D[from_name + from_email]
  B --> E[reply_to]
  C --> F[Basic auth header]
  D --> G[Payload field: from]
  E --> H[Payload field: replyTo]
```

## Basic Usage

```python
from django.contrib.sites.models import Site
from django_forwardemail.models import EmailConfiguration

site = Site.objects.get(domain="example.com")

config = EmailConfiguration.objects.create(
    site=site,
    api_key="fe_live_primary",
    from_email="noreply@example.com",
    from_name="Example",
    reply_to="support@example.com",
)

print(str(config))
```

## Advanced Usage

This pattern is useful in provisioning scripts or tenant onboarding flows where you need idempotent updates:

```python
from django.contrib.sites.models import Site
from django_forwardemail.models import EmailConfiguration

site, _ = Site.objects.get_or_create(
    domain="billing.example.com",
    defaults={"name": "Billing"},
)

config, created = EmailConfiguration.objects.update_or_create(
    site=site,
    defaults={
        "api_key": "fe_live_billing",
        "from_email": "billing@example.com",
        "from_name": "Example Billing",
        "reply_to": "accounts@example.com",
    },
)

print(created, config.from_email)
```

<Callout type="warn">Do not create more than one row per site through custom SQL or disabled constraint checks. The service uses `.get(site=site)`, so duplicate rows will turn a configuration problem into a runtime exception instead of a deterministic fallback.</Callout>

<Accordions>
<Accordion title="Why a ForeignKey plus uniqueness instead of OneToOneField">
The package uses `ForeignKey(Site, on_delete=models.CASCADE)` with `unique_together` rather than declaring a `OneToOneField`. Functionally, the result is still one configuration per site, but the explicit uniqueness constraint is visible in both the model and the migration. This makes the single-row assumption easy to audit because the service code and the schema tell the same story. A `OneToOneField` would also have worked, but it would not change how the service retrieves data or how the admin presents the record.
</Accordion>
<Accordion title="Database-backed config versus settings-based config">
Storing the API key in the database increases operational flexibility because each site can rotate credentials independently and staff can update sender metadata without code changes. The trade-off is that an app instance cannot send mail correctly until migrations have run and the table contains the right row. In contrast, environment variables make bootstrapping simpler for single-site apps but collapse all sites into one sender identity unless you build your own routing layer. This package chose database state because multi-site behavior is the primary feature, not an edge case.
</Accordion>
</Accordions>

## Practical Checks

- Ensure `django.contrib.sites` is installed and `SITE_ID` is valid.
- Create the `Site` row before creating the configuration row.
- Restrict admin access, because the model stores the API key in plain database form.
- When rotating credentials, update the row first and then test with a live send.

Next: read [Site Resolution](/docs/site-resolution) to see how the service decides which configuration row to load.
