"""
Pydantic models for the Email Service.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List


class SmtpProfile(BaseModel):
    """SMTP credentials for one email account."""
    profile_id: str
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    from_email: EmailStr
    from_name: str = "Email Service"
    verify_ssl: bool = True


class EmailMessage(BaseModel):
    """An email to be sent."""
    to: List[EmailStr]
    subject: str
    text: Optional[str] = None
    html: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None


class SendRequest(EmailMessage):
    """API request body for sending an email via a named profile."""
    profile: Optional[str] = None   # Falls back to default from .env if omitted
