"""
Tests for django-forwardemail address helpers.
"""

import pytest

from django_forwardemail.utils import sanitize_address


class TestSanitizeAddress:
    @pytest.mark.parametrize(
        "addr,expected",
        [
            ("user@example.com", "user@example.com"),
            ("Name <user@example.com>", "Name <user@example.com>"),
            ('"Name, Inc" <user@example.com>', '"Name, Inc" <user@example.com>'),
            ("  user@example.com  ", "user@example.com"),
            ("(comment) user@example.com", "user@example.com"),
            ('"quoted local"@example.com', '"quoted local"@example.com'),
            ("user.name+tag@sub.example.co.uk", "user.name+tag@sub.example.co.uk"),
            ("user@[192.168.0.1]", "user@[192.168.0.1]"),
            ("webmaster@localhost", "webmaster@localhost"),
            ("Dr. Who <user@example.com>", '"Dr. Who" <user@example.com>'),
        ],
    )
    def test_plain_addresses(self, addr, expected):
        assert sanitize_address(addr) == expected

    def test_non_ascii_display_name_is_rfc2047_encoded(self):
        assert (
            sanitize_address("Ünï <user@example.com>")
            == "=?utf-8?b?w5xuw68=?= <user@example.com>"
        )

    def test_non_ascii_local_part_is_rfc2047_encoded(self):
        assert (
            sanitize_address("üser@example.com") == "=?utf-8?b?w7xzZXI=?=@example.com"
        )

    def test_non_ascii_domain_is_punycoded(self):
        assert sanitize_address("user@ünï.com") == "user@xn--n-nga1b.com"

    def test_tuple_form(self):
        assert sanitize_address(("Name", "user@example.com")) == (
            "Name <user@example.com>"
        )

    def test_tuple_form_requires_domain(self):
        with pytest.raises(ValueError, match="Invalid address"):
            sanitize_address(("Name", "nodomain"))

    @pytest.mark.parametrize(
        "addr",
        [
            "",
            "one@example.com, two@example.com",
        ],
    )
    def test_invalid_addresses_raise(self, addr):
        with pytest.raises(ValueError, match="Invalid address"):
            sanitize_address(addr)

    @pytest.mark.parametrize(
        "addr",
        [
            # The stdlib parser recovers from all of these rather than
            # raising, so the helper has to reject them itself: without that,
            # the first truncates to "user@example.com" and the rest format as
            # the null address "<>".
            "user@example.com trailing garbage",
            "user@example..com",
            "user@.com",
            "user@example.com.",
            "user@a@example.com",
            "not-an-address",
            "Name <user@example.com",
            "user@example.com>",
            "<>",
            "Name <>",
            ("Name", "@example.com"),
            ("Name", "user@"),
        ],
    )
    def test_malformed_addresses_are_not_silently_repaired(self, addr):
        with pytest.raises(ValueError, match="Invalid address"):
            sanitize_address(addr)

    @pytest.mark.parametrize(
        "addr",
        [
            "user@example.com\nX-Injected: 1",
            "user@example.com\r\nX-Injected: 1",
            ("Bad\nName", "user@example.com"),
        ],
    )
    def test_header_injection_is_rejected(self, addr):
        with pytest.raises(ValueError, match="newlines"):
            sanitize_address(addr)

    def test_custom_encoding(self):
        assert (
            sanitize_address("Ünï <user@example.com>", "iso-8859-1")
            == "=?iso-8859-1?q?=DCn=EF?= <user@example.com>"
        )
