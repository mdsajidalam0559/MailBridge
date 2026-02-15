"""
Self-Hosted Email API — FastAPI Server

Run:
    python main.py
    # or
    uvicorn main:app --reload --port 9001
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from email_service import send, profiles, SmtpProfile, SendRequest, settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# ─── Lifespan ────────────────────────────────────────────────────────────────


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
        logger.info("Default profile '%s' registered from .env", settings.default_profile_id)
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

    try:
        result = await send(req, profile)
        return {"message": "Email sent", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Profile Management ──────────────────────────────────────────────────────


@app.post("/profiles", tags=["Profiles"])
async def add_profile(req: SmtpProfile):
    """Register or update an SMTP profile."""
    return profiles.add(req)


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
