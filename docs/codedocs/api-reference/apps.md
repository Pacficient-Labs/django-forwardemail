---
title: "App Configuration API"
description: "Reference for the Django AppConfig used by django-forwardemail."
---

Public import path:

```python
from django_forwardemail.apps import DjangoForwardEmailConfig
```

The implementation lives in `django_forwardemail/apps.py`.

## Overview

`DjangoForwardEmailConfig` is the package's `AppConfig`. It registers the Django app name, verbose label, and default auto field.

### Class Signature

```python
class DjangoForwardEmailConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_forwardemail"
    verbose_name = "Django ForwardEmail"

    def ready(self):
        pass
```

## Attributes

| Attribute | Type | Value | Description |
|-----------|------|-------|-------------|
| `default_auto_field` | `str` | `"django.db.models.BigAutoField"` | Default primary key type for models in this app. |
| `name` | `str` | `"django_forwardemail"` | Django application label and import path. |
| `verbose_name` | `str` | `"Django ForwardEmail"` | Human-readable name shown in admin and app listings. |

## `ready`

```python
def ready(self) -> None
```

The method currently does nothing beyond existing as a hook for future initialization. There are no signals or startup side effects registered here in version `1.0.1`.

Usage example:

```python
INSTALLED_APPS = [
    "django.contrib.sites",
    "django_forwardemail",
]
```

## Package Metadata

The package root in `django_forwardemail/__init__.py` also exposes:

```python
__version__ = "1.0.1"
__author__ = "PacNPal and Pacficient Labs"
__email__ = "support@pacficient.com"
default_app_config = "django_forwardemail.apps.DjangoForwardEmailConfig"
```

Those values are useful for package consumers and compatibility with older Django app-loading behavior.

## Why This Module Matters

This page is short because the module is short, but it still defines the package boundary that Django imports at startup. Knowing that `ready()` is currently a no-op is useful operationally: there are no hidden signals, no background registrations, and no startup side effects to debug when the app is installed. The `default_app_config` export in `__init__.py` also explains why the package remains compatible with older app-loading patterns even though newer Django versions usually discover `AppConfig` automatically. That makes startup behavior predictable, which matters when you are debugging deployment order, migration state, or admin registration issues in new environments.

Related pages: [Getting Started](/docs) and [Architecture](/docs/architecture).
