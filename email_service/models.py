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
    from_email: str
    from_name: str = "Email Service"


class EmailMessage(BaseModel):
    """An email to be sent."""
    to: List[EmailStr]
    subject: str
    text: Optional[str] = None
    html: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None


class SendRequest(BaseModel):
    """API request body for sending an email via a named profile."""
    profile: Optional[str] = None   # Falls back to default from .env if omitted
    to: List[EmailStr]
    subject: str
    text: Optional[str] = None
    html: Optional[str] = None
    from_name: Optional[str] = None


class ProfileRequest(BaseModel):
    """API request body for registering an SMTP profile."""
    profile_id: str
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    from_email: str
    from_name: str = "Email Service"
