"""
Profile Manager — CRUD operations for SMTP profiles.
Profiles are stored in a local JSON file.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Optional

from .config import settings
from .models import SmtpProfile

logger = logging.getLogger(__name__)

_lock = threading.Lock()


def _profiles_path() -> Path:
    """Resolve the profiles file path relative to the project root."""
    path = Path(settings.profiles_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path
    return path


def _load_profiles() -> dict:
    """Load all profiles from disk."""
    path = _profiles_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_profiles(profiles: dict) -> None:
    """Persist profiles to disk."""
    with open(_profiles_path(), "w") as f:
        json.dump(profiles, f, indent=2)


def get(profile_id: str) -> Optional[SmtpProfile]:
    """Retrieve a single profile by its ID."""
    with _lock:
        data = _load_profiles().get(profile_id)
    return SmtpProfile(**data) if data else None


def list_all() -> list[dict]:
    """List all profiles with passwords masked."""
    with _lock:
        profiles = _load_profiles()
    return [
        {**data, "smtp_password": "****"}
        for data in profiles.values()
    ]


def add(profile: SmtpProfile) -> dict:
    """Add or update an SMTP profile."""
    with _lock:
        profiles = _load_profiles()
        profiles[profile.profile_id] = profile.model_dump()
        _save_profiles(profiles)
    logger.info("Profile '%s' saved", profile.profile_id)
    return {"status": "saved", "profile_id": profile.profile_id}


def delete(profile_id: str) -> dict:
    """Delete a profile by its ID."""
    with _lock:
        profiles = _load_profiles()
        if profile_id not in profiles:
            return {"status": "not_found", "profile_id": profile_id}
        del profiles[profile_id]
        _save_profiles(profiles)
    logger.info("Profile '%s' deleted", profile_id)
    return {"status": "deleted", "profile_id": profile_id}
