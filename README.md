# Megeb+ Backend

Django REST Framework backend for the Megeb+ nutrition platform, handling authentication, OTP-based phone verification, and user management.

## Tech Stack

- Django 6.1 + Django REST Framework
- PostgreSQL (hosted on Neon)
- JWT authentication via `djangorestframework-simplejwt`
- AfroMessage for SMS/OTP delivery
- Pipenv for dependency management

## Features

- Phone-based registration with OTP verification
- Login with JWT access/refresh tokens (blocked until phone is verified)
- Forgot password / reset password via OTP
- Resend OTP support
- Health profile storage for authenticated users

## Project Structure

Megeb_Plus_Backend/
├── accounts/ # Authentication app: register, login, OTP, JWT
│ ├── models.py # User model (phone-based auth) and PhoneOTP model
│ ├── serializers.py
│ ├── views.py
│ ├── urls.py
│ └── utils.py # OTP generation and AfroMessage SMS sending
├── health/ # Health profile app
├── config/ # Django project settings and root URLs
├── Pipfile / Pipfile.lock
└── manage.py


## Setup

1. Clone the repo and create a virtual environment:

python -m venv venv
.\venv\Scripts\activate


2. Install dependencies:

pipenv install


3. Create a `.env` file in the project root with:

DATABASE_URL=your_postgres_connection_string
AFROMESSAGE_TOKEN=your_afromessage_token
AFROMESSAGE_IDENTIFIER_ID=your_afromessage_identifier_id


   > Note: without valid AfroMessage credentials, `send_sms()` falls back to a
   > mocked mode that prints the OTP to the console instead of sending a real SMS —
   > useful for local development without SMS credits.

4. Run migrations:

python manage.py migrate


5. Start the development server:

python manage.py runserver


   Server runs at `http://127.0.0.1:8000/`.

## Authentication Flow

**Registration:**
1. `POST /register/` — creates an inactive, unverified user and sends an OTP
2. `POST /verify-otp/` (purpose: `register`) — verifies the code, activates the account, and returns JWT tokens
3. User is now logged in and can call `/login/` on future visits

**Password reset:**
1. `POST /forgot-password/` — sends an OTP for password reset
2. Collect the OTP from the user, then submit it together with the new password to `/reset-password/` in one call (the OTP is validated as part of that request, not separately)

## API Endpoints

All endpoints are under `/api/auth/`:

| Endpoint | Method | Auth required | Description |
|---|---|---|---|
| `/register/` | POST | No | Register a new user, sends OTP |
| `/verify-otp/` | POST | No | Verify phone with OTP code |
| `/resend-otp/` | POST | No | Resend OTP code |
| `/login/` | POST | No | Login with phone + password |
| `/forgot-password/` | POST | No | Request password reset OTP |
| `/reset-password/` | POST | No | Reset password with OTP + new password |
| `/me/` | GET | Yes (JWT) | Get current authenticated user |
| `/health-profile/` | POST | Yes (JWT) | Save/update health profile |
| `/token/refresh/` | POST | No | Refresh JWT access token |

## Testing

python manage.py test


## Notes

- Phone numbers are the primary login identifier (`USERNAME_FIELD = "phone"`), not email.
- New accounts are created with `is_active=False` until OTP verification completes.
- If AfroMessage rejects a phone number as "unverified contact" — this happens on trial/beta AfroMessage accounts, which require manually verifying test numbers in the AfroMessage dashboard before SMS can be delivered to them.