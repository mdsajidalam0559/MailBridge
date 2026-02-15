"""
Email Service — A reusable module for sending emails via any SMTP provider.

Usage as a module:
    from email_service import send, profiles, SmtpProfile, EmailMessage

    # Register a profile
    profiles.add(SmtpProfile(
        profile_id="my_gmail",
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_user="you@gmail.com",
        smtp_password="app-password",
        from_email="you@gmail.com",
        from_name="My App",
    ))

    # Send an email
    await send(
        EmailMessage(to=["client@example.com"], subject="Hi!", text="Hello world"),
        profiles.get("my_gmail"),
    )

Usage as a standalone server:
    uvicorn main:app --reload
"""

from .models import SmtpProfile, EmailMessage, SendRequest
from .sender import send
from . import profiles
from .config import settings

__all__ = [
    "send",
    "profiles",
    "SmtpProfile",
    "EmailMessage",
    "SendRequest",
    "settings",
]
