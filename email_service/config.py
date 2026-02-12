"""
Configuration loader for the Email Service.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env"""

    # Default SMTP profile (auto-registered on startup)
    default_profile_id: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = ""
    from_name: str = "Email Service"

    # App settings
    profiles_file: str = "profiles.json"
    api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    @property
    def has_default_profile(self) -> bool:
        return bool(self.default_profile_id and self.smtp_host and self.smtp_user and self.smtp_password)


settings = Settings()
