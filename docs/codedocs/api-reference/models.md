---
title: "EmailConfiguration API"
description: "Reference for the Django model that stores ForwardEmail credentials and sender defaults."
---

Public import path:

```python
from django_forwardemail.models import EmailConfiguration
```

The implementation lives in `django_forwardemail/models.py`.

## Overview

`EmailConfiguration` is the only persistent model in the package. Every successful email send depends on resolving one `Site` to one `EmailConfiguration`.

### Model Definition

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

### Meta Options

```python
class Meta:
    verbose_name = "Email Configuration"
    verbose_name_plural = "Email Configurations"
    unique_together = [["site"]]
```

## Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `api_key` | `models.CharField(max_length=255)` | — | ForwardEmail API key used for Basic auth. |
| `from_email` | `models.EmailField()` | — | Default sender address. |
| `from_name` | `models.CharField(max_length=255)` | — | Display name combined with `from_email` when the service builds the `from` field. |
| `reply_to` | `models.EmailField()` | — | Default reply-to address when callers do not override it. |
| `site` | `models.ForeignKey(Site, on_delete=models.CASCADE)` | — | Django Site this configuration applies to. |
| `created_at` | `models.DateTimeField(auto_now_add=True)` | auto-set | Timestamp set on creation. |
| `updated_at` | `models.DateTimeField(auto_now=True)` | auto-set | Timestamp updated on each save. |

## Public Behavior

### `__str__`

```python
def __str__(self) -> str
```

Returns:

```python
f"{self.from_name} <{self.from_email}> ({self.site.domain})"
```

Usage example:

```python
config = EmailConfiguration.objects.get(site__domain="example.com")
print(str(config))
```

## Common Patterns

Create a row:

```python
from django.contrib.sites.models import Site
from django_forwardemail.models import EmailConfiguration

site = Site.objects.get(domain="example.com")

EmailConfiguration.objects.create(
    site=site,
    api_key="fe_live_xxx",
    from_email="noreply@example.com",
    from_name="Example",
    reply_to="support@example.com",
)
```

Idempotent provisioning:

```python
EmailConfiguration.objects.update_or_create(
    site=site,
    defaults={
        "api_key": "fe_live_rotated",
        "from_email": "noreply@example.com",
        "from_name": "Example",
        "reply_to": "support@example.com",
    },
)
```

## Source-backed Notes

- The migration enforces one configuration per site through `AlterUniqueTogether`.
- The tests in `tests/test_models.py` verify creation, string representation, uniqueness, email validation, and multi-site usage.
- `on_delete=models.CASCADE` means deleting a `Site` also deletes the matching email configuration.

Related pages: [Email Configuration](/docs/email-configuration) and [Multi-Site Deployments](/docs/guides/multi-site-deployments).
