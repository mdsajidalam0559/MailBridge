"""
Test script — quick test for the Email API.

Usage:
    1. Make sure .env has your credentials
    2. Start server:  uvicorn main:app --reload
    3. Run:           python test_email.py
"""

import requests

BASE = "http://localhost:8000"


def test_health():
    print("🏥 Health check...")
    r = requests.get(f"{BASE}/")
    print(f"   {r.json()}\n")


def test_list_profiles():
    print("📋 Profiles (auto-loaded from .env):")
    for p in requests.get(f"{BASE}/profiles").json():
        print(f"   → {p['profile_id']}: {p['from_email']} via {p['smtp_host']}")
    print()


def test_send(to_email):
    print(f"🚀 Sending to {to_email} (using default profile)...")
    r = requests.post(f"{BASE}/email/send", json={
        "to": [to_email],
        "subject": "Test — Self-Hosted Email API ✅",
        "html": "<h1>🎉 It Works!</h1><p>Sent from your self-hosted Email API.</p>",
    })
    print(f"   {'✅' if r.ok else '❌'} {r.json()}\n")


if __name__ == "__main__":
    print("=" * 50)
    print("  Email API — Quick Test")
    print("=" * 50 + "\n")

    test_health()
    test_list_profiles()
    test_send("mdsajidalam0559@gmail.com")  # ← change this

    print("=" * 50)
    print("  Done! Check your inbox.")
    print("=" * 50)
