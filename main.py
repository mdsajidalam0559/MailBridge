"""
Self-Hosted Email API — FastAPI Server

Run:
    uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from email_service import send, profiles, SmtpProfile, EmailMessage, SendRequest, ProfileRequest
from email_service.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Auto-register the default profile from .env on startup."""
    if settings.has_default_profile:
        profiles.add(SmtpProfile(
            profile_id=settings.default_profile_id,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_password=settings.smtp_password,
            from_email=settings.from_email or settings.smtp_user,
            from_name=settings.from_name,
        ))
        print(f"✅ Default profile '{settings.default_profile_id}' registered from .env")
    yield


app = FastAPI(
    title="Self-Hosted Email API",
    description="Send emails from any email account (Gmail, Outlook, Zoho, custom domains).",
    version="2.0.0",
    lifespan=lifespan,
)


# ─── Email Sending ────────────────────────────────────────────────────────────


@app.post("/email/send", tags=["Email"])
async def send_email(req: SendRequest):
    """Send an email using a registered SMTP profile."""
    if not req.text and not req.html:
        raise HTTPException(status_code=400, detail="Provide 'text' or 'html' body.")

    # Use default profile if none specified
    profile_id = req.profile or settings.default_profile_id
    if not profile_id:
        raise HTTPException(status_code=400, detail="No profile specified and no default configured.")

    profile = profiles.get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found. Register it via POST /profiles.")

    message = EmailMessage(
        to=req.to,
        subject=req.subject,
        text=req.text,
        html=req.html,
        from_name=req.from_name,
    )

    try:
        result = await send(message, profile)
        return {"status": "success", "message": "Email sent", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Profile Management ──────────────────────────────────────────────────────


@app.post("/profiles", tags=["Profiles"])
async def add_profile(req: ProfileRequest):
    """Register or update an SMTP profile."""
    profile = SmtpProfile(**req.model_dump())
    return profiles.add(profile)


@app.get("/profiles", tags=["Profiles"])
async def list_profiles():
    """List all registered SMTP profiles (passwords masked)."""
    return profiles.list_all()


@app.delete("/profiles/{profile_id}", tags=["Profiles"])
async def remove_profile(profile_id: str):
    """Delete an SMTP profile."""
    result = profiles.delete(profile_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found.")
    return result


# ─── Health ───────────────────────────────────────────────────────────────────


@app.get("/", tags=["Health"])
def health():
    return {"status": "running", "service": "Self-Hosted Email API v2.0"}
