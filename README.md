# Self-Hosted Email API

Send emails from **any email account** via a simple REST API or Python import.

## Quick Start

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure (add your SMTP credentials)
cp .env.example .env
# Edit .env with your email details

# Run
uvicorn main:app --reload
```

## Running Tests

To test the email sending functionality, ensure the server is running and then execute the test script:

```bash
# Install test dependencies (included in requirements.txt)
pip install -r requirements.txt

# Run the test script
python test_email.py
```

Open **http://localhost:8000/docs** for interactive Swagger UI.

## .env Configuration

```bash
DEFAULT_PROFILE_ID=nomoosh          # Profile name
SMTP_HOST=smtp.hostinger.com        # Your SMTP server
SMTP_PORT=465                       # 465 (SSL) or 587 (TLS)
SMTP_USER=support@nomoosh.com       # Your email
SMTP_PASSWORD=your-password         # App password or account password
FROM_EMAIL=support@nomoosh.com      # Sender address
FROM_NAME=Nomoosh Support           # Sender display name
```

The default profile is **auto-registered on startup** — no extra steps needed.

## Send an Email

```bash
# Minimal — uses the default profile from .env
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["client@example.com"],
    "subject": "Hello!",
    "html": "<h1>Hi!</h1><p>Sent from my API</p>"
  }'
```

## Multiple Accounts

Register additional profiles via API:

```bash
curl -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "gmail",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "you@gmail.com",
    "smtp_password": "app-password",
    "from_email": "you@gmail.com",
    "from_name": "My Gmail"
  }'
```

Then send using that profile:

```bash
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "gmail",
    "to": ["someone@example.com"],
    "subject": "From Gmail",
    "text": "Hello from Gmail!"
  }'
```

## Use as a Python Module

Copy `email_service/` into your project:

```python
import asyncio
from email_service import send, profiles, EmailMessage

async def main():
    profile = profiles.get("nomoosh")
    await send(
        EmailMessage(to=["client@example.com"], subject="Hi!", text="Hello"),
        profile,
    )

asyncio.run(main())
```

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/email/send` | Send an email |
| `POST` | `/profiles` | Add/update SMTP profile |
| `GET` | `/profiles` | List all profiles |
| `DELETE` | `/profiles/{id}` | Delete a profile |
| `GET` | `/` | Health check |

## SMTP Reference

| Provider | Host | Port |
|---|---|---|
| Gmail / Workspace | `smtp.gmail.com` | 587 |
| Outlook / O365 | `smtp.office365.com` | 587 |
| Hostinger | `smtp.hostinger.com` | 465 |
| Zoho | `smtp.zoho.com` | 465 |
| GoDaddy | `smtpout.secureserver.net` | 465 |
| Yahoo | `smtp.mail.yahoo.com` | 587 |

## Project Structure

```
├── email_service/        ← Reusable Python package
│   ├── __init__.py       # Public exports
│   ├── config.py         # Settings (.env loader)
│   ├── models.py         # Pydantic models
│   ├── profiles.py       # Profile CRUD
│   └── sender.py         # Async email sender
├── main.py               # FastAPI server
├── test_email.py         # Test script
├── .env                  # Your credentials (git-ignored)
├── .env.example          # Template
└── requirements.txt
```
