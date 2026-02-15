# Self-Hosted Email API

A lightweight, provider-agnostic email service built with FastAPI. Supports sending emails through any SMTP provider (Gmail, Outlook, Zoho, Hostinger, custom domains, etc.) via a REST API or as an importable Python module.

## Features

- REST API for sending emails with HTML and plain text support
- SMTP profile management (register and store accounts)
- Auto-registration of a default SMTP profile from environment variables on startup
- Async email delivery using `aiosmtplib`
- Docker support
- Usable as a standalone server or as an embedded Python module

## Prerequisites

- Python 3.10+ (for local setup) or Docker
- SMTP credentials from your email provider (e.g., Gmail App Password)

## Installation

### Using Docker (recommended)

```bash
git clone <repository-url>
cd sms_service_personal

cp .env.example .env
# Edit .env with your SMTP credentials

docker compose up -d
```

The service will be available at `http://localhost:9001`.

To rebuild after code changes:

```bash
docker compose up -d --build
```

To stop:

```bash
docker compose down
```

### Manual Setup

```bash
git clone <repository-url>
cd sms_service_personal

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy the example environment file and fill in your SMTP credentials:

```bash
cp .env.example .env
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DEFAULT_PROFILE_ID` | Name for the auto-registered default profile | |
| `SMTP_HOST` | SMTP server hostname | |
| `SMTP_PORT` | SMTP port (`465` for SSL, `587` for STARTTLS) | `587` |
| `SMTP_USER` | SMTP login username | |
| `SMTP_PASSWORD` | SMTP login password or app password | |
| `FROM_EMAIL` | Sender email address | |
| `FROM_NAME` | Sender display name | `Email Service` |
| `VERIFY_SSL` | Verify SMTP server SSL certificate | `true` |
| `PROFILES_FILE` | Path to the JSON file for storing profiles | `profiles.json` |
| `HOST` | Server bind address | `127.0.0.1` |
| `PORT` | Server port | `9001` |

## Usage

### Starting the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --port 9001
```

The interactive API documentation is available at `http://localhost:9001/docs`.

### Sending an Email

The sender details (`from_email`, `from_name`) and SMTP credentials are automatically pulled from the default profile configured in `.env`.

```bash
curl -X POST http://localhost:9001/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Order Confirmation",
    "html": "<h1>Thank you for your order</h1><p>Your order has been confirmed.</p>"
  }'
```

Plain text email:

```bash
curl -X POST http://localhost:9001/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Hello",
    "text": "Plain text email body"
  }'
```

### Managing SMTP Profiles

**Register a profile:**

```bash
curl -X POST http://localhost:9001/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "gmail",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "you@gmail.com",
    "smtp_password": "app-password",
    "from_email": "you@gmail.com",
    "from_name": "My App",
    "verify_ssl": true
  }'
```

The `verify_ssl` field defaults to `true`. Set it to `false` only if your SMTP server uses a self-signed certificate.

**List all profiles:**

```bash
curl http://localhost:9001/profiles
```

Passwords are masked in the response.

**Delete a profile:**

```bash
curl -X DELETE http://localhost:9001/profiles/gmail
```

### Using as a Python Module

The `email_service` package can be imported directly into any Python project:

```python
import asyncio
from email_service import send, profiles, SmtpProfile, EmailMessage

async def main():
    profiles.add(SmtpProfile(
        profile_id="my_gmail",
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_user="you@gmail.com",
        smtp_password="app-password",
        from_email="you@gmail.com",
        from_name="My App",
    ))

    profile = profiles.get("my_gmail")
    await send(
        EmailMessage(to=["recipient@example.com"], subject="Hello", text="Hello world"),
        profile,
    )

asyncio.run(main())
```

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/email/send` | Send an email |
| `POST` | `/profiles` | Register or update an SMTP profile |
| `GET` | `/profiles` | List all profiles (passwords masked) |
| `DELETE` | `/profiles/{profile_id}` | Delete a profile |

## Supported SMTP Providers

| Provider | Host | Port |
|---|---|---|
| Gmail / Google Workspace | `smtp.gmail.com` | 587 |
| Outlook / Office 365 | `smtp.office365.com` | 587 |
| Hostinger | `smtp.hostinger.com` | 465 |
| Zoho | `smtp.zoho.com` | 465 |
| GoDaddy | `smtpout.secureserver.net` | 465 |
| Yahoo | `smtp.mail.yahoo.com` | 587 |

Any SMTP-compatible provider can be used by specifying the appropriate host and port.

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

A manual smoke test script (`test_all_endpoints.py`) is also included for testing against a live server:

```bash
python test_all_endpoints.py
```

## Project Structure

```
email_service/
    __init__.py         Public API exports
    config.py           Settings loader (reads .env)
    models.py           Pydantic data models
    profiles.py         Profile CRUD with thread-safe file persistence
    sender.py           Async SMTP email sender
tests/
    test_api.py         Pytest suite (profiles, sending)
main.py                 FastAPI application entry point
test_all_endpoints.py   Manual smoke test script
Dockerfile              Container image definition
docker-compose.yml      Docker Compose configuration
.env.example            Environment variable template
requirements.txt        Python dependencies
```

## License

This project is provided as-is for personal and internal use.
