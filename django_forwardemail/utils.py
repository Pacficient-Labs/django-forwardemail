"""
Version-independent helpers used by the backend and the service layer.

Django deprecated its internal ``django.core.mail.message.sanitize_address()``
in Django 6.0 (``RemovedInDjango70Warning``) and removes it in Django 7.0. The
deprecation message points at Python's own email package, so the replacement
below is built on :class:`email.headerregistry.Address` and produces the same
output Django's helper did.
"""

from email.errors import HeaderParseError
from email.header import Header
from email.headerregistry import Address, AddressHeader, HeaderRegistry
from email.utils import formataddr
from typing import cast

# Reused across calls; HeaderRegistry instances are stateless parsers.
_header_registry = HeaderRegistry()


def _parse_mailbox(addr: str) -> tuple[str, str, str]:
    """
    Parse a single mailbox into its ``(display name, local part, domain)``.

    Args:
        addr: Address string such as ``"Name <user@example.com>"``

    Returns:
        Tuple of display name, local part and domain

    Raises:
        ValueError: If the string is not exactly one mailbox
    """
    try:
        header = cast(AddressHeader, _header_registry("to", addr))
        addresses = header.addresses
    except (HeaderParseError, ValueError, IndexError) as exc:
        raise ValueError(f'Invalid address "{addr}"') from exc

    if len(addresses) != 1:
        raise ValueError(f'Invalid address "{addr}"')

    mailbox = addresses[0]
    return mailbox.display_name or "", mailbox.username or "", mailbox.domain or ""


def sanitize_address(addr: str | tuple[str, str], encoding: str = "utf-8") -> str:
    """
    Format an email address for use in a message header.

    Drop-in replacement for Django's deprecated ``sanitize_address()``, built on
    the stdlib email package so it keeps working on Django 7.0 and later.
    Non-ASCII display names and local parts are RFC 2047 encoded, and non-ASCII
    domains are converted to Punycode.

    Args:
        addr: Either an address string (``"Name <user@example.com>"`` or
            ``"user@example.com"``) or a ``(name, address)`` tuple
        encoding: Charset used for non-ASCII parts

    Returns:
        The formatted address

    Raises:
        ValueError: If the address is missing, malformed, or contains newlines
    """
    if isinstance(addr, tuple):
        display_name, address = addr
        address = str(address)
        if "@" not in address:
            raise ValueError(f'Invalid address "{address}"')
        localpart, domain = address.rsplit("@", 1)
    else:
        addr = str(addr)
        # Check the raw value too: the parser silently drops embedded newlines
        # rather than rejecting them, which would mask a header injection.
        if "\n" in addr or "\r" in addr:
            raise ValueError("Invalid address; address parts cannot contain newlines.")
        display_name, localpart, domain = _parse_mailbox(addr)

    display_name = str(display_name)
    if any("\n" in part or "\r" in part for part in (display_name, localpart, domain)):
        raise ValueError("Invalid address; address parts cannot contain newlines.")

    # Avoid a UTF-8 encoded word when the part is plain ASCII.
    try:
        display_name.encode("ascii")
        display_name = Header(display_name).encode()
    except UnicodeEncodeError:
        display_name = Header(display_name, encoding).encode()
    try:
        localpart.encode("ascii")
    except UnicodeEncodeError:
        localpart = Header(localpart, encoding).encode()
    # UnicodeError (a ValueError) is raised for domains the IDNA codec rejects.
    domain = domain.encode("idna").decode("ascii")

    addr_spec = Address(username=localpart, domain=domain).addr_spec
    return formataddr((display_name, addr_spec))
