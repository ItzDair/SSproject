Multi-Factor Authentication (MFA) Service
Overview
This project provides a secure Multi-Factor Authentication (MFA) system with:

Time-based One-Time Password (TOTP) generation and verification

Multiple notification channels (Email and Telegram)

Rate limiting for security

Health monitoring endpoints

The system consists of two main services:

MFA Server: Handles OTP generation and verification

Notification Service: Handles message delivery through various channels

Client → MFA Server (request-otp/verify) → Notification Service → Telegram/Email

Prerequisites
Python 3.7+

Docker (for containerized deployment)

Environment variables configured (see .env.example below)

Installation
Clone the repository

Create and activate a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
Install dependencies:

bash
pip install -r requirements.txt
Configuration
Create a .env file with the following variables:

ini
# MFA Server Configuration
FLASK_SECRET_KEY=your-secret-key
RATE_LIMIT=200 per day

# User Secrets
Dair_SECRET=base32secret3232
BOB_SECRET=base32secret3232

# User Contact Info
DAIR_TELEGRAM_ID=123456789
Dair_email=dair@example.com
BOB_TELEGRAM_ID=987654321
BOB_EMAIL=bob@example.com

# Notification Service Configuration
TELEGRAM_TOKEN=your-telegram-bot-token
EMAIL_SENDER=your@email.com
EMAIL_PASSWORD=your-email-password
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=465
Running the Services
Development Mode
Start the MFA Server:

bash
python mfa_server.py
Start the Notification Service (in a separate terminal):

bash
python app.py
Production Mode
Using Gunicorn (included in requirements):

bash
gunicorn -w 4 -b 0.0.0.0:6000 mfa_server:app
gunicorn -w 4 -b 0.0.0.0:6001 app:app
Docker
Build the images:

bash
docker build -t mfa-server .
docker build -t notification-service .
Run with Docker Compose (create a docker-compose.yml file first)

API Endpoints
MFA Server
POST /request-otp

Request body: {"username": "dair"}

Returns: OTP sent via configured channels

POST /verify

Request body: {"username": "dair", "token": "123456"}

Returns: {"valid": true/false}

GET /healthcheck

Returns service status

Notification Service
POST /send

Request body: {"channel": "email/telegram", "recipient": "address", "message": "text"}

Returns delivery status

GET /healthcheck

Returns service status

Security Features
Rate limiting on all endpoints

TOTP with configurable validity window

Secure secret storage in environment variables

Retry mechanism for email delivery

Comprehensive logging

Testing
Example curl commands:

Request OTP:

bash
curl -X POST http://localhost:6000/request-otp -H "Content-Type: application/json" -d '{"username": "dair"}'
Verify OTP:

bash
curl -X POST http://localhost:6000/verify -H "Content-Type: application/json" -d '{"username": "dair", "token": "123456"}'
Monitoring
Check service health:

bash
curl http://localhost:6000/healthcheck
curl http://localhost:6001/healthcheck
Logging
All operations are logged with timestamps and relevant details. Check your console or configured log files.
