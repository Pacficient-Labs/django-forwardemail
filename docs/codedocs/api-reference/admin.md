---
title: "Admin API"
description: "Reference for the Django admin integration that manages EmailConfiguration records."
---

Public import path:

```python
from django_forwardemail.admin import EmailConfigurationAdmin
```

The implementation lives in `django_forwardemail/admin.py`.

## Overview

`EmailConfigurationAdmin` is registered with `@admin.register(EmailConfiguration)`. Installing the app makes the model editable in Django admin without additional setup.

### Class Signature

```python
class EmailConfigurationAdmin(admin.ModelAdmin):
```

## Class Attributes

| Attribute | Value | Description |
|-----------|-------|-------------|
| `list_display` | `("site", "from_name", "from_email", "reply_to", "updated_at")` | Columns shown in the list view. |
| `list_select_related` | `("site",)` | Avoids extra queries when rendering `site`. |
| `search_fields` | `("site__domain", "from_name", "from_email", "reply_to")` | Searchable fields in admin. |
| `readonly_fields` | `("created_at", "updated_at")` | Timestamps are visible but not editable. |
| `list_filter` | `("site", "updated_at", "created_at")` | Sidebar filters for list view. |
| `fieldsets` | Site, Email Settings, Timestamps | Groups the form into operational sections. |

## Public Methods

### `get_queryset`

```python
def get_queryset(self, request: HttpRequest) -> QuerySet[EmailConfiguration]
```

Returns the default queryset with `select_related("site")` applied.

Usage example:

```python
# Called by Django admin automatically; no manual invocation is usually needed.
```

### `formfield_for_foreignkey`

```python
def formfield_for_foreignkey(
    self,
    db_field: ForeignKey,
    request: HttpRequest,
    **kwargs: object,
) -> Any
```

When the foreign key field is `site`, it replaces the queryset with `Site.objects.all().order_by("domain")` so the dropdown is easier to scan in large installations.

Usage example:

```python
# Called by Django admin automatically when rendering the form.
```

## Operational Use

Admin is the simplest way to manage sender defaults:

1. Open Django admin.
2. Go to `Django ForwardEmail -> Email Configurations`.
3. Select the site and enter the API key, sender email, sender name, and reply-to value.

Because the model stores the API key, admin access should be limited to trusted staff roles.

## Practical Implications

The admin class is intentionally small because most of the package logic belongs in the service layer, not in the editing UI. Its query optimization still matters in real projects, though, because large Django admin screens can degenerate into repeated `Site` lookups if `select_related("site")` is missing. Ordering the site dropdown by domain is also a meaningful operational choice for multi-domain teams, since it makes the intended configuration easier to find and reduces accidental edits.

Related pages: [Email Configuration](/docs/email-configuration) and [Architecture](/docs/architecture).
