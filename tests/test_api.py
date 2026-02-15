"""
Tests for the Email API endpoints.
Uses httpx + FastAPI TestClient with mocked SMTP sending.
"""

import pytest
from unittest.mock import patch, AsyncMock

from httpx import AsyncClient, ASGITransport

from email_service import settings
from main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ─── Health ───────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_health(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"


# ─── Profiles ─────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_add_and_list_profile(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "profiles_file", str(tmp_path / "profiles.json"))

    profile = {
        "profile_id": "test_gmail",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "user@gmail.com",
        "smtp_password": "secret",
        "from_email": "user@gmail.com",
        "from_name": "Test",
    }

    r = await client.post("/profiles", json=profile)
    assert r.status_code == 200
    assert r.json()["status"] == "saved"

    r = await client.get("/profiles")
    items = r.json()
    assert len(items) == 1
    assert items[0]["profile_id"] == "test_gmail"
    assert items[0]["smtp_password"] == "****"


@pytest.mark.anyio
async def test_delete_profile(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "profiles_file", str(tmp_path / "profiles.json"))

    profile = {
        "profile_id": "to_delete",
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "u@example.com",
        "smtp_password": "pw",
        "from_email": "u@example.com",
    }
    await client.post("/profiles", json=profile)

    r = await client.delete("/profiles/to_delete")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"


@pytest.mark.anyio
async def test_delete_nonexistent_profile(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "profiles_file", str(tmp_path / "profiles.json"))

    r = await client.delete("/profiles/nope")
    assert r.status_code == 404


# ─── Email Sending ────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_send_email_success(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "profiles_file", str(tmp_path / "profiles.json"))

    profile = {
        "profile_id": "sender",
        "smtp_host": "smtp.example.com",
        "smtp_port": 465,
        "smtp_user": "u@example.com",
        "smtp_password": "pw",
        "from_email": "u@example.com",
    }
    await client.post("/profiles", json=profile)

    with patch("email_service.sender.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        r = await client.post("/email/send", json={
            "profile": "sender",
            "to": ["recipient@example.com"],
            "subject": "Test",
            "text": "Hello",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "success"
        mock_send.assert_called_once()


@pytest.mark.anyio
async def test_send_email_no_body(client):
    r = await client.post("/email/send", json={
        "to": ["recipient@example.com"],
        "subject": "Test",
        "profile": "x",
    })
    assert r.status_code == 400
    assert "text" in r.json()["detail"].lower() or "html" in r.json()["detail"].lower()


@pytest.mark.anyio
async def test_send_email_unknown_profile(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "profiles_file", str(tmp_path / "profiles.json"))
    monkeypatch.setattr(settings, "default_profile_id", "")

    r = await client.post("/email/send", json={
        "profile": "nonexistent",
        "to": ["recipient@example.com"],
        "subject": "Test",
        "text": "Hello",
    })
    assert r.status_code == 404
