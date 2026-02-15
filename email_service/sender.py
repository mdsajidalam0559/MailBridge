"""
Email Sender — sends emails using a given SMTP profile.
Works with any email provider (Gmail, Outlook, Zoho, custom domains, etc.)
"""

import logging
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

import aiosmtplib

from .models import SmtpProfile, EmailMessage

logger = logging.getLogger(__name__)


def _create_ssl_context(*, verify: bool = True) -> ssl.SSLContext:
    """Create an SSL context. Verifies certificates by default."""
    ctx = ssl.create_default_context()
    if not verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


async def send(message: EmailMessage, profile: SmtpProfile) -> dict:
    """
    Send an email using the provided SMTP profile.

    TLS mode is auto-detected from the port:
      - 465  → Implicit SSL/TLS
      - 587  → STARTTLS
      - other → No encryption (not recommended)

    Args:
        message: The email content (to, subject, text/html).
        profile: The SMTP credentials to use.

    Returns:
        {"status": "success", "profile_used": "<profile_id>"}

    Raises:
        Exception: On SMTP connection or authentication failure.
    """
    use_tls = profile.smtp_port == 465
    start_tls = profile.smtp_port == 587
    tls_context = _create_ssl_context(verify=profile.verify_ssl)

    sender_email = message.from_email or profile.from_email
    sender_name = message.from_name or profile.from_name

    mime = MIMEMultipart("alternative")
    mime["From"] = formataddr((sender_name, sender_email))
    mime["To"] = ", ".join(message.to)
    mime["Subject"] = message.subject

    if message.text:
        mime.attach(MIMEText(message.text, "plain"))
    if message.html:
        mime.attach(MIMEText(message.html, "html"))

    try:
        await aiosmtplib.send(
            mime,
            hostname=profile.smtp_host,
            port=profile.smtp_port,
            username=profile.smtp_user,
            password=profile.smtp_password,
            use_tls=use_tls,
            start_tls=start_tls,
            tls_context=tls_context,
        )
        logger.info("Email sent to %s via %s (%s)", message.to, profile.profile_id, profile.smtp_host)
        return {"status": "success", "profile_used": profile.profile_id}
    except Exception as e:
        logger.error("Failed via %s: %s", profile.profile_id, e)
        raise
