"""
Tests for django-forwardemail email backend.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.test import override_settings

from django_forwardemail.models import EmailConfiguration

BACKEND = "django_forwardemail.backends.ForwardEmailBackend"


def make_config(site=None):
    if site is None:
        site = Site.objects.get_current()
    return EmailConfiguration.objects.create(
        site=site,
        api_key="test-api-key",
        from_email="sender@example.com",
        from_name="Test Sender",
        reply_to="reply@example.com",
    )


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
