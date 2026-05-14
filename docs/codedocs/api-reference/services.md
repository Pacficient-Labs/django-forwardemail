---
title: "ForwardEmailService API"
description: "Reference for the direct service API, including send_email, extract_email, constants, and the EmailService alias."
---

Public import paths:

```python
from django_forwardemail.services import ForwardEmailService, EmailService
```

The implementation lives in `django_forwardemail/services.py`.

## Overview

`ForwardEmailService` is the package's canonical execution API. The Django backend delegates to it, so its behavior defines most of the library's runtime semantics.

### Class Signature

```python
class ForwardEmailService:
    DEFAULT_BASE_URL = "https://api.forwardemail.net"
```

### Constants

| Name | Type | Value | Description |
|------|------|-------|-------------|
| `DEFAULT_BASE_URL` | `str` | `"https://api.forwardemail.net"` | Default API host when `base_url` and `FORWARD_EMAIL_BASE_URL` are both unset. |

## `send_email`

```python
@classmethod
def send_email(
    cls,
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

Sends one email through the ForwardEmail API after resolving the active site and loading `EmailConfiguration`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `to` | `str` | — | Recipient email address. |
| `subject` | `str` | — | Subject line sent to ForwardEmail. |
| `text` | `str` | — | Plain-text body. |
| `from_email` | `str \| None` | `None` | Optional sender override. If it lacks a display name, the configured `from_name` is prepended. |
| `html` | `str \| None` | `None` | Optional HTML body. Added to the JSON payload only when present. |
| `reply_to` | `str \| None` | `None` | Optional reply-to override. Falls back to the model value and is sanitized with `sanitize_address`. |
| `request` | `HttpRequest \| None` | `None` | Request used for `get_current_site(request)` when `site` is not provided. |
| `site` | `Site \| None` | `None` | Explicit site to use for configuration lookup. |
| `base_url` | `str \| None` | `None` | Per-call API host override. |

Returns:

```python
dict[str, Any]
```

Raises:

- `django.core.exceptions.ImproperlyConfigured` when no usable `Site` can be resolved or the site has no `EmailConfiguration`.
- `Exception` for non-200 HTTP responses and `requests` transport errors.

Usage example:

```python
from django.contrib.sites.models import Site
from django_forwardemail.services import ForwardEmailService

site = Site.objects.get(domain="example.com")

result = ForwardEmailService.send_email(
    to="user@example.com",
    subject="Welcome",
    text="Welcome to Example.",
    html="<h1>Welcome to Example.</h1>",
    site=site,
)
```

Combined pattern with explicit base URL override for tests:

```python
ForwardEmailService.send_email(
    to="user@example.com",
    subject="Smoke test",
    text="Testing a non-default endpoint.",
    site=site,
    base_url="https://api-staging.forwardemail.net",
)
```

## `extract_email`

```python
@staticmethod
def extract_email(email_string: str) -> str
```

Extracts the bare email address from either `"Name <email@domain.com>"` or an already plain address.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `email_string` | `str` | — | Address string that may include a display name. |

Returns:

```python
str
```

Usage example:

```python
from django_forwardemail.services import ForwardEmailService

assert ForwardEmailService.extract_email("Ops <ops@example.com>") == "ops@example.com"
assert ForwardEmailService.extract_email("ops@example.com") == "ops@example.com"
```

## `EmailService` Alias

```python
EmailService = ForwardEmailService
```

This alias exists for backward compatibility. New code should import `ForwardEmailService`, but existing code using `EmailService` behaves the same because both names reference the same class object.

Usage example:

```python
from django_forwardemail.services import EmailService

EmailService.send_email(
    to="user@example.com",
    subject="Legacy import path",
    text="This still works.",
)
```

## Source-backed Behavior Notes

- The service builds a Basic auth header from `f"{api_key}:"`, base64-encoded.
- The request target is always `f"{api_base_url}/v1/emails"`.
- The HTTP timeout is fixed at `60` seconds.
- `DEBUG=True` enables request and response logging through the `django_forwardemail` logger.

Related pages: [Architecture](/docs/architecture) and [Send with the Service Class](/docs/guides/send-with-service).
