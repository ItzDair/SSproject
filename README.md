
# Multi-Factor Authentication (MFA) Service

## Overview

This project provides a secure Multi-Factor Authentication (MFA) system with:

* Time-based One-Time Password (TOTP) generation and verification
* Multiple notification channels (Email and Telegram)
* Rate limiting for enhanced security
* Health monitoring endpoints

### Components

* **MFA Server**: Handles OTP generation and verification
* **Notification Service**: Delivers messages via email and Telegram

---

## Architecture

```
Client → MFA Server (/request-otp, /verify)
                 ↓
       Notification Service
            ↓         ↓
       Telegram     Email
```

---

## Prerequisites

* Python 3.7 or higher
* Docker (for containerized deployment)
* A configured `.env` file (see example below)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-user/social_media_mfa.git
cd social_media_mfa
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # On Linux/Mac
venv\Scripts\activate           # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file with the following variables:

```ini
# MFA Server Configuration
FLASK_SECRET_KEY=your-secret-key
RATE_LIMIT=200 per day

# User Secrets
DAIR_SECRET=base32secret3232
BOB_SECRET=base32secret3232

# User Contact Info
DAIR_TELEGRAM_ID=123456789
DAIR_EMAIL=dair@example.com
BOB_TELEGRAM_ID=987654321
BOB_EMAIL=bob@example.com

# Notification Service Configuration
TELEGRAM_TOKEN=your-telegram-bot-token
EMAIL_SENDER=your@email.com
EMAIL_PASSWORD=your-email-password
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=465
```

---

## Running the Services

### Development Mode

Start the MFA Server:

```bash
python mfa_server.py
```

Start the Notification Service (in a separate terminal):

```bash
python app.py
```

### Production Mode (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:6000 mfa_server:app
gunicorn -w 4 -b 0.0.0.0:6001 app:app
```

### Docker Deployment

Build the images:

```bash
docker build -t mfa-server .
docker build -t notification-service .
```

Use Docker Compose (after creating `docker-compose.yml`):

```bash
docker-compose up --build
```

---

## API Endpoints

### MFA Server

* `POST /request-otp`
  Request Body:

  ```json
  { "username": "dair" }
  ```

* `POST /verify`
  Request Body:

  ```json
  { "username": "dair", "token": "123456" }
  ```

* `GET /healthcheck`
  Returns service status.

### Notification Service

* `POST /send`
  Request Body:

  ```json
  {
    "channel": "email" or "telegram",
    "recipient": "address",
    "message": "text"
  }
  ```

* `GET /healthcheck`
  Returns service status.

---

## Security Features

* Rate limiting on all endpoints
* TOTP with configurable validity window
* Secure secret storage using environment variables
* Retry mechanism for email delivery
* Logging of key operations

---

## Testing

Example curl commands:

Request OTP:

```bash
curl -X POST http://localhost:6000/request-otp \
  -H "Content-Type: application/json" \
  -d '{"username": "dair"}'
```

Verify OTP:

```bash
curl -X POST http://localhost:6000/verify \
  -H "Content-Type: application/json" \
  -d '{"username": "dair", "token": "123456"}'
```

---

## Monitoring

Health check endpoints:

```bash
curl http://localhost:6000/healthcheck
curl http://localhost:6001/healthcheck
```

---

## Logging

All operations are logged with timestamps and contextual information. Logs can be viewed in the console or directed to log files depending on your setup.

