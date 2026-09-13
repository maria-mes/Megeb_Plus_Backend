# Megeb Plus — Backend

Megeb Plus is an AI-powered nutrition and wellness platform. This repository contains the **Django REST Framework backend** that powers both the React Native mobile app and the Next.js web admin panel.

> ⚠️ Some details below (exact package versions, `.env` variable names, deployment specifics) are marked as **TODO** — fill these in with the real values from your `requirements.txt` / `settings.py` before sharing this README, since they weren't available when this draft was generated.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Apps](#apps)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database](#database)
- [Authentication](#authentication)
- [API Overview](#api-overview)
- [Known Issues / Open Items](#known-issues--open-items)
- [Contributors](#contributors)

---

## Overview

Megeb Plus helps users track nutrition, log meals and activity, connect with nutritionists for consultations, and get AI-generated wellness suggestions. The platform has three client surfaces:

- **Mobile app** (React Native) — the primary client-facing product
- **Web frontend** (Next.js) — nutritionist-facing and public-facing pages
- **Admin panel** (Next.js) — internal dashboard for platform administrators

This backend serves all three over a shared REST API.

---

## Tech Stack

- **Framework:** Django + Django REST Framework
- **Database:** PostgreSQL (hosted on [Neon](https://neon.tech), pooled connection)
- **Auth:** JWT (`CustomTokenObtainPairView`), email OTP for registration/password reset
- **AI:** Google Gemini API (AI-generated dashboard suggestions)
- **Email:** Gmail SMTP
- **Payments:** StarPay (Ethiopian payment gateway integration)

<!-- TODO: confirm exact package versions — check requirements.txt -->

---

## Project Structure

```
megeb-plus-backend/
├── accounts/         # Users, auth, OTP registration, staff applications
├── health/           # Health profiles, food catalog, food diary, activity/water/weight logs, AI suggestions
├── appointments/      # Appointment booking + slot-based availability
├── consultations/     # Consultation records tied to appointments
├── admin_panel/       # Admin-only views: users, clients, nutritionists, reports, dashboard, food database, settings
├── payments/          # Payment transactions, platform fee handling (StarPay integration)
├── vendors/           # Food vendor applications and profiles
├── <project_root>/    # settings.py, root urls.py
└── manage.py
```

<!-- TODO: replace <project_root> with the actual settings package name -->

---

## Apps

### `accounts`
User model and authentication. Handles:
- Email OTP registration via `PendingRegistration`
- Unified login via an `identifier` field (email or phone)
- Forgot-password flow via OTP
- Staff (nutritionist) applications with file uploads + admin approval flow

### `health`
The core nutrition/wellness domain. Owns:
- `HealthProfile` — onboarding data (age, gender, height/weight, activity level, diet preference, goals) and server-computed nutrition targets (calories, macros, water target)
- `WeightLog`, `WaterLog`, `ExerciseLog` — daily logging, one entry per user per day
- `Food` — shared nutrition catalog (per-100g values), used by both the mobile food picker and the admin Food Database page
- `FoodEntry` — food diary entries, with nutrition snapshotted at log time so historical entries don't drift if the catalog changes later
- `AISuggestion` — cached, one-per-day AI-generated dashboard tip (Gemini API)
- Streak tracking (`current_streak_days`, `longest_streak_days`), maintained automatically whenever a log is created/updated/deleted

### `appointments`
Slot-based appointment booking between clients and nutritionists.

### `consultations`
Consultation records (notes, outcomes) tied to a completed appointment.

### `admin_panel`
Internal-only endpoints for the admin dashboard: user/client/nutritionist management, platform reports, dashboard stats, the shared Food Database, platform settings, and admin's own profile/password management. Mounted at `/api/auth/admin/`.

### `payments`
StarPay gateway integration, platform fee split logic, and admin-facing payment monitoring.

### `vendors`
Food vendor applications (approval flow with AI-assisted verification) and vendor profiles/products.

---

## Getting Started

```powershell
# Clone the repo
git clone <repo-url>
cd megeb-plus-backend

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see below)
Copy-Item .env.example .env

# Run migrations
python manage.py migrate

# Create a superuser (for Django admin / initial admin account)
python manage.py createsuperuser

# Run the dev server
python manage.py runserver
```

<!-- TODO: confirm these commands match your actual setup, especially if there's a custom management command for seeding the Food catalog -->

---

## Environment Variables

<!-- TODO: fill in the real keys from your .env / settings.py — placeholders below are guesses based on the stack described -->

```env
SECRET_KEY=
DEBUG=

DATABASE_URL=          # Neon pooled Postgres connection string

EMAIL_HOST_USER=        # Gmail SMTP
EMAIL_HOST_PASSWORD=

GEMINI_API_KEY=         # Google Gemini API, for AI suggestions

STARPAY_API_KEY=        # Payment gateway
STARPAY_SECRET=

JWT_SIGNING_KEY=
```

---

## Database

- PostgreSQL, hosted on Neon (`*.aws.neon.tech`), accessed via a pooled connection string
- `CONN_MAX_AGE=0` is set to avoid connection instability against the pooler
- Run `python manage.py makemigrations <app>` after any model change, then `python manage.py migrate`

---

## Authentication

- **Login:** `POST /api/auth/login/` via `CustomTokenObtainPairView` — accepts a single `identifier` field (email or phone)
- **Registration:** Email OTP flow via `PendingRegistration` — a pending record is created and cleared once the OTP is verified, at which point tokens are issued
- **Password reset:** OTP-based forgot-password flow
- **Admin routes:** mounted separately at `/api/auth/admin/`, protected by `IsAdminRole`

---

## API Overview

Full endpoint reference: see `admin_panel_api.md` for the complete admin panel API (all endpoints, request/response shapes, and known gaps).

Representative endpoints:

| Area | Endpoint | Notes |
|---|---|---|
| Auth | `POST /api/auth/login/` | Unified login |
| Profile | `GET/PATCH /profile/` | Composite of User + HealthProfile fields |
| Nutrition goals | `GET /nutrition/goals/` | Auto-computed targets |
| Food diary | `/food-diary/` | Logged meals, nutrition computed server-side |
| Activities | `/activities/` | Exercise logs, calories computed server-side |
| Admin — Food | `GET/POST /api/auth/admin/food` | Shared `health.Food` catalog |
| Admin — Dashboard | `GET /api/auth/admin/dashboard/stats` | Headline stat cards |
| Admin — Reports | `GET /api/auth/admin/reports/overview` | Platform-wide metrics |

All admin panel routes are prefixed with `/api/auth/admin/`.

---

## Known Issues / Open Items

- Mismatched enum vocabularies between mobile onboarding and backend choice fields (`activity_level`, `fasting_preference`, `health_goal`) — needs a shared source of truth
- `djangorestframework-camel-case` not yet added everywhere — some serializers (e.g. `admin_panel`) manually camelCase field names instead
- Vendor food application flow (list/detail/approve-reject) is scoped to a teammate, not yet built
- Admin Food Database page: the "Add Food Item" POST flow isn't wired up on the frontend yet — the backend endpoint (`/api/auth/admin/food`) supports it, but `page.tsx` currently uses local mock state
- `Food.serving_label` is a **display-only** field — it does not scale the per-100g nutrition values, since there's no structured grams input on the current admin form

---

## Contributors

- **Radyat Daniel** 
- **Mariamawit Messay** 
 
---

