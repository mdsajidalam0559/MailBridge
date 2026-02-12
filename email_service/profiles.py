"""
Profile Manager — CRUD operations for SMTP profiles.
Profiles are stored in a local JSON file.
"""

import json
import os
from typing import Optional

from .config import settings
from .models import SmtpProfile


def _load_profiles() -> dict:
    """Load all profiles from disk."""
    path = settings.profiles_file
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_profiles(profiles: dict) -> None:
    """Persist profiles to disk."""
    with open(settings.profiles_file, "w") as f:
        json.dump(profiles, f, indent=2)


def get(profile_id: str) -> Optional[SmtpProfile]:
    """Retrieve a single profile by its ID."""
    data = _load_profiles().get(profile_id)
    return SmtpProfile(**data) if data else None


def list_all() -> list[dict]:
    """List all profiles with passwords masked."""
    return [
        {**data, "smtp_password": "****"}
        for data in _load_profiles().values()
    ]


def add(profile: SmtpProfile) -> dict:
    """Add or update an SMTP profile."""
    profiles = _load_profiles()
    profiles[profile.profile_id] = profile.model_dump()
    _save_profiles(profiles)
    return {"status": "saved", "profile_id": profile.profile_id}


def delete(profile_id: str) -> dict:
    """Delete a profile by its ID."""
    profiles = _load_profiles()
    if profile_id not in profiles:
        return {"status": "not_found", "profile_id": profile_id}
    del profiles[profile_id]
    _save_profiles(profiles)
    return {"status": "deleted", "profile_id": profile_id}
