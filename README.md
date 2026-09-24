# LinkStudio

A self-hostable link-in-bio and appointment-booking platform for creators, built with Django 5, MariaDB/MySQL, and Bootstrap 5.

Creators get a single shareable link (`/<username>/`) where followers can browse active links, connect on social media, download contact info (.vcf), send inquiries, and book 1-on-1 services directly into the creator's schedule.

---

## Architecture & Tech Stack

- **Backend:** Python 3.12+, Django 5, Django REST Framework
- **Database:** MariaDB / MySQL (or SQLite for local frontend dev)
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, Poppins typography (with offline local backup)
- **Media Storage:** Cloudinary for user-uploaded avatars, cover banners, and link thumbnails
- **Static Assets:** WhiteNoise with compressed manifest storage
- **Email Delivery:** Brevo (formerly Sendinblue) via SMTP relay

---

## Core Features

- **Public Creator Profile (`/<username>/`):** Responsive, mobile-first bio page with theme support, custom cover banners, verified badge, and one-click "Save Contact" (.vcf vCard 3.0).
- **Link Management:** Order links via drag-and-drop, toggle visibility, and track outgoing click counts through `/l/<id>/`.
- **Service Bookings & Calendar:** Creators define services (duration, price) and weekly availability hours. Time slots are generated dynamically and reserved atomically using database row locks (`select_for_update`) to prevent double-booking.
- **Lead & Contact Capture:** Integrated contact box on public profiles with dashboard management, search filtering, and formula-sanitized CSV export.
- **Appearance Studio:** 9 preset color themes, customizable backgrounds (colors, gradients, Cloudinary photo uploads with blur/darkness overlays), custom button shapes, shadows, and hover animations, complete with a live-updating mobile preview.
- **Creator Dashboard (`/dashboard/`):** Unified workspace scoped strictly to each creator's account.

---

## Email System (Brevo SMTP)

LinkStudio uses **Brevo** (`smtp-relay.brevo.com`) for transactional email delivery.

### Configured Email Flows

| Event | Recipient | Trigger / Purpose |
|---|---|---|
| **Account Confirmation** | Creator (`User.email`) | Sent immediately upon sign-up with links to their profile and dashboard. |
| **Password Reset** | Creator (`User.email`) | Standard Django tokenized reset link to recover access. |
| **New Booking Request** | Creator (`public_email` $\rightarrow$ `User.email`) | Dispatched when a visitor books a time slot, including date, service, and contact details. |
| **New Contact Inquiry** | Creator (`public_email` $\rightarrow$ `User.email`) | Dispatched when a visitor leaves a message on the creator's public contact form. |
| **Booking Status Update** | Visitor (`visitor_email`) | Dispatched when a creator confirms, rejects, or cancels a booking. Includes custom instructions if confirmed. |

### Failure Isolation
All outgoing email calls run inside `try/except` blocks and log delivery errors. If Brevo or the network encounters downtime, the underlying booking, contact submission, or registration still succeeds without surfacing an unhandled error to the user.

### Brevo Environment Variables
Add the following to your `.env` file (or Render dashboard):

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-brevo-login-email@example.com
EMAIL_HOST_PASSWORD=your-brevo-smtp-key
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=LinkStudio <noreply@yourdomain.com>
```

> **Note:** During local development with `DEBUG=True`, Django defaults to the console email backend (`django.core.mail.backends.console.EmailBackend`), outputting all messages to your terminal instead of sending actual emails.

---

## Local Development

### 1. Prerequisites
- Python 3.12+
- MariaDB or MySQL (recommended), or SQLite for UI testing
- Cloudinary account (free tier works)
- Brevo account (free tier provides 300 emails/day)

### 2. Setup Virtual Environment
```bash
git clone https://github.com/<your-username>/linkstudio.git
cd linkstudio

python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

> **Note on SQLite (`DB_ENGINE=sqlite`):**
> SQLite is suitable **only for rapid local UI and template work**. Because SQLite does not support `select_for_update()` row locking (Django treats it as a no-op), the atomic double-booking guard cannot enforce lock exclusivity under concurrent requests. For concurrency testing, use MariaDB or MySQL.

### 5. Run Migrations & Seed Data
```bash
python manage.py migrate
python scripts/seed_demo_data.py
```

### 6. Start the Server
```bash
python manage.py runserver
```

Open your browser to:
- **Home:** http://127.0.0.1:8000/
- **Creator Demo:** http://127.0.0.1:8000/eddiescott/
- **Dashboard:** http://127.0.0.1:8000/dashboard/

---

## Running Tests

Run the full automated test suite (includes authentication, vCard RFC escaping, CSV formula sanitization, rate limiting, booking transitions, and email dispatch):

```bash
python manage.py test
```

---

## Production Deployment (Render)

This repository includes a [`render.yaml`](./render.yaml) blueprint and [`build.sh`](./build.sh) script for one-click deployment to [Render](https://render.com/).

### Deployment Steps:
1. Push your repository to GitHub.
2. In the Render Dashboard, select **New +** $\rightarrow$ **Blueprint** and connect your repository.
3. Render detects `render.yaml` and provisions:
   - **Build Command:** `./build.sh` (runs `pip install`, `collectstatic`, and `migrate`)
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
4. Set your production secrets under **Environment Variables**:
   - `SECRET_KEY`
   - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
5. Click **Apply** to deploy.

---
