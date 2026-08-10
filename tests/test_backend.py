"""
Tests for django-forwardemail email backend.
"""

import warnings
from unittest.mock import MagicMock, patch

import django
import pytest
from django.contrib.sites.models import Site
from django.core import mail
from django.core.mail import EmailMessage, send_mail
from django.test import override_settings

from django_forwardemail.backends import ForwardEmailBackend
from django_forwardemail.models import EmailConfiguration

BACKEND = "django_forwardemail.backends.ForwardEmailBackend"


def make_config(site=None, **overrides):
    if site is None:
        site = Site.objects.get_current()
    kwargs = {
        "api_key": "test-api-key",
        "from_email": "sender@example.com",
        "from_name": "Test Sender",
        "reply_to": "reply@example.com",
    }
    kwargs.update(overrides)
    return EmailConfiguration.objects.create(site=site, **kwargs)


def mock_200():
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"queued": True}
    return response


@pytest.mark.django_db
class TestForwardEmailBackend:
    def test_send_mail_without_explicit_site(self):
        """Regression test for #1: send_mail must work without passing site/request."""
        make_config()

        with patch("django_forwardemail.services.requests.post", return_value=mock_200()) as mock_post:
            with override_settings(EMAIL_BACKEND=BACKEND):
                result = send_mail(
                    "Subject here",
                    "Here is the message.",
                    "sender@example.com",
                    ["recipient@example.com"],
                    fail_silently=False,
                )

        assert result == 1
        mock_post.assert_called_once()
        payload = mock_post.call_args.kwargs["json"]
        assert payload["to"] == "recipient@example.com"
        assert payload["subject"] == "Subject here"

    def test_send_mail_no_config_raises(self):
        """Without an EmailConfiguration the backend must surface the error."""
        with override_settings(EMAIL_BACKEND=BACKEND):
            with pytest.raises(Exception, match="Email configuration is missing"):
                send_mail(
                    "Subject",
                    "Body",
                    "sender@example.com",
                    ["recipient@example.com"],
                    fail_silently=False,
                )

    def test_send_emits_no_deprecation_warnings(self):
        """Regression test for #18: no Django 7.0 deprecations on the send path.

        ``sanitize_address()`` and ``EmailMessage.connection`` both raise
        ``RemovedInDjango70Warning`` (a ``PendingDeprecationWarning``) when used
        under Django 6.1+.
        """
        make_config()
        message = EmailMessage(
            subject="Subject",
            body="Body",
            from_email="sender@example.com",
            to=["recipient@example.com"],
        )

        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            warnings.simplefilter("error", PendingDeprecationWarning)
            with patch(
                "django_forwardemail.services.requests.post", return_value=mock_200()
            ):
                sent = ForwardEmailBackend(fail_silently=False).send_messages([message])

        assert sent == 1

    def test_from_email_display_name_is_normalized(self):
        """A named from_email is reduced to the address and re-labelled."""
        make_config()
        message = EmailMessage(
            subject="Subject",
            body="Body",
            from_email="Someone <sender@example.com>",
            to=["recipient@example.com"],
            reply_to=["Reply Person <reply@example.com>"],
        )

        with patch(
            "django_forwardemail.services.requests.post", return_value=mock_200()
        ) as mock_post:
            ForwardEmailBackend(fail_silently=False).send_messages([message])

        payload = mock_post.call_args.kwargs["json"]
        assert payload["from"] == "Test Sender <sender@example.com>"
        assert payload["replyTo"] == "Reply Person <reply@example.com>"

    def test_site_from_message_connection_is_preferred(self):
        """A site set on the message's own connection still wins over the backend."""
        default_site = Site.objects.get_current()
        other_site = Site.objects.create(domain="other.example.com", name="Other")
        make_config(default_site)
        make_config(other_site, reply_to="other-reply@other.example.com")

        message = EmailMessage(
            subject="Subject", body="Body", to=["recipient@example.com"]
        )
        # Setting EmailMessage.connection warns under Django 6.1+; this test
        # only cares that the backend still reads whatever is there.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            message.connection = ForwardEmailBackend(site=other_site)

        with patch(
            "django_forwardemail.services.requests.post", return_value=mock_200()
        ) as mock_post:
            ForwardEmailBackend(site=default_site).send_messages([message])

        payload = mock_post.call_args.kwargs["json"]
        assert payload["replyTo"] == "other-reply@other.example.com"

    @pytest.mark.skipif(
        django.VERSION < (6, 1), reason="MAILERS was added in Django 6.1"
    )
    def test_backend_works_as_a_mailers_alias(self):
        """Django 7.0 replaces EMAIL_BACKEND with the MAILERS setting."""
        make_config()
        message = EmailMessage(
            subject="Subject",
            body="Body",
            from_email="sender@example.com",
            to=["recipient@example.com"],
        )

        with override_settings(MAILERS={"default": {"BACKEND": BACKEND}}):
            connection = mail.mailers["default"]
            with patch(
                "django_forwardemail.services.requests.post", return_value=mock_200()
            ):
                sent = connection.send_messages([message])

        assert sent == 1
        assert connection.alias == "default"
