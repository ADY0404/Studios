# LinkStudio — Modern Creator Link-in-Bio & Booking Platform

LinkStudio is a production-grade, human-crafted creator and link-in-bio SaaS platform built with **Django**, **MariaDB**, **Bootstrap 5.3**, **WhiteNoise**, and **Django REST Framework**.

---

## 🌟 Key Features

### 1. Account & Security System
- Full Django native authentication (Register, Login, Logout, Password Reset, Password Change).
- Creator username management with strict URL safety, formatting regex, and reserved keyword protection (`admin`, `dashboard`, `login`, `register`, `api`, `static`, etc.).
- Strict role separation: platform administrators manage the site via the Django Admin Console (`/admin/`), while creators have dedicated dashboard workspaces (`/dashboard/`).
- Permanent account self-deletion with confirmation safeguard.

### 2. Public Creator Profile (`/<username>/`)
- Mobile-first, responsive public page with customizable branding.
- Optional wide Cover Banner header with avatar overlapping the seam.
- Verified Creator badge and custom headline tagline.
- Avatar styling: shapes (*Circle*, *Rounded Squircle*, *Sharp Square*) and border rings (*White Frame*, *Accent Ring*, *Luminous Glow*, *None*).
- **"Save My Contact"** feature: Generates and downloads a standardized `.vcf` vCard 3.0 file with one click.
- Supports customizable profile alignment (Centered or Left-aligned).

### 3. Dynamic Link Management
- Add, edit, toggle, and delete links with titles, URLs, descriptions, custom thumbnails, and icons.
- **Drag-and-Drop Reordering**: Interactive HTML5 drag-and-drop integrated with an asynchronous REST API (`/dashboard/links/api/reorder/`) to persist order without duplicate positions.
- **Outbound Click Analytics**: Clicks are tracked through atomic `/l/<id>/` redirects.

### 4. Social Media Connections
- Connect platforms with recognizable SVG icons: Instagram, TikTok, YouTube, X/Twitter, LinkedIn, GitHub, Threads, Spotify, Facebook, Twitch, and Discord.
- Flexible placement: Top (under bio) or Bottom (above footer).
- Visual styles: Official brand colors, monochrome, or frosted glass badges.

### 5. Scheduling & Intelligent Double-Booking Prevention
- **Services Manager**: Define services with duration (15m, 30m, 60m, etc.), price (USD), description, and instructions.
- **Weekly Availability**: Configure active hours for each day of the week (Monday through Sunday).
- **Slot Calculation Engine**: Dynamically calculates future available slots based on service duration, operating hours, and active reservations.
- **Atomic Double-Booking Guard**: All booking reservations are executed inside atomic transactions with database-level row locks (`select_for_update`) to prevent concurrent booking conflicts.
- **Dashboard Hub**: Approve, reject, complete, or cancel booking requests with status filters.

### 6. Visitor Lead & Contact Capture
- Built-in voluntary contact submission box on creator bio pages.
- Lead management in dashboard with keyword search and **CSV Export** for email marketing.

### 7. Appearance Studio & Live Phone Preview
- **9 Curated Designer Palettes**:
  - *Minimalist Snow*
  - *Midnight Obsidian*
  - *Sunset Reverie*
  - *Matcha & Sage*
  - *Neo-Brutalist Pop*
  - *Neon Cyberpunk*
  - *Velvet Cherry*
  - *Ocean Aurora*
  - *Paper & Ink Editorial*
- **Full Customization Overrides**:
  - Background (Solid Color, Custom CSS Gradient, or Custom Photo upload with darkness filter overlay & blur sliders)
  - Button Shapes (*Smooth Rounded*, *Full Pill*, *Sharp Square*)
  - Button Styles (*Frosted Glass*, *Solid Fill*, *Soft Tint*, *Outline*, *Hard 3D*, *Ambient Glow*)
  - Card Shadows (*None*, *Subtle*, *Elevated*, *Color Glow*, *Hard 3D*)
  - Hover Animations (*Float Lift*, *Gentle Zoom*, *Glow Pulse*, *None*)
  - Typography (*Inter*, *Plus Jakarta Sans*, *Outfit*, *DM Sans*, *Poppins*, *Space Grotesk*, *Syne*, *Playfair Display*, *JetBrains Mono*)
- **Interactive Live Preview**: Simulated iPhone device frame that synchronizes in real time as you adjust settings.

### 8. Full Admin Command Center (`/admin/`)
- Comprehensive Django Admin with multi-model inlines (Links, Socials, Services, and Appearance directly on Profile).
- Quick inline list editing for links, services, socials, and bookings.
- Administrative bulk actions: Verify/unverify creators, enable/disable links, confirm bookings, and export inquiries to CSV.

---

## 🚀 Deployment on Render

This repository includes a `render.yaml` blueprint and a `build.sh` script for zero-config deployment.

### Step 1: Push Code to GitHub
1. Create a new repository on [GitHub](https://github.com/new) (e.g. `linkstudio`).
2. Add your GitHub remote and push:
```bash
git remote add origin https://github.com/<your-username>/linkstudio.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Blueprint**.
2. Connect your GitHub repository.
3. Render will automatically detect `render.yaml` and configure the Web Service with:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
4. Set your `DB_PASSWORD` environment variable in the Render Dashboard (from your `.env` file).
5. Click **Apply** to deploy!

---

## 💻 Local Development

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/<your-username>/linkstudio.git
cd linkstudio
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your database credentials:
```bash
cp .env.example .env
```

### 4. Database Setup & Migrations
```bash
python manage.py migrate
python scripts/seed_demo_data.py
```

### 5. Start Development Server
```bash
python manage.py runserver
```
Visit:
- Home: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Creator Demo: [http://127.0.0.1:8000/eddiescott/](http://127.0.0.1:8000/eddiescott/)
- Creator Dashboard: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- Admin Console: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
