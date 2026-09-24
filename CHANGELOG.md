# Changelog & Hardening Summary — LinkStudio

## [Security & Correctness Hardening Pass] — September 2026

This release improves LinkStudio's production security, data protection, reliability, and code maintainability without altering visual styles or breaking existing workflows.

---

### Summary of Changes

#### 1. Production Security Headers & Key Protection
- **Enforced HTTPS & Cookie Security**: Session and CSRF cookies are now strictly flagged as `Secure` in production, with automatic SSL redirects and HSTS (HTTP Strict Transport Security) enabled.
- **Reverse Proxy Header**: Configured `SECURE_PROXY_SSL_HEADER` so Render’s upstream TLS termination is properly recognized.
- **Fail-Fast Secret Key**: Django will raise an `ImproperlyConfigured` startup error if `SECRET_KEY` is missing in production, preventing unintended insecure defaults.

#### 2. CSV Injection Prevention (OWASP Compliance)
- **Contact Export Sanitization**: Implemented `sanitize_csv_field` to prefix formulas and commands (`=`, `+`, `-`, `@`, tab, newline) with a single quote (`'`), neutralizing spreadsheet formula injection attacks when exporting contacts to CSV.

#### 3. vCard RFC 6350 Escaping
- **Special Character Escaping**: Updated vCard generator to escape backslashes, semicolons, and commas in contact name fields and notes per the vCard 3.0 specification, ensuring downloaded `.vcf` files open properly on all phones and operating systems.

#### 4. Booking State Machine
- **Strict Status Transitions**: Added explicit validation rules (`can_transition_to`) to prevent invalid booking status jumps (e.g. jumping out of completed, cancelled, or rejected states). Invalid transitions now display a clear warning message rather than corrupting state.

#### 5. Email Notifications
- **Automated Alerts**: Creators receive email alerts upon new booking requests and contact inquiries. Visitors receive immediate status updates when their booking is confirmed, rejected, or cancelled.
- **Resilient Delivery**: All email notifications are wrapped in error handling and logging so an email delivery issue never disrupts user bookings or inquiries.

#### 6. Rate Limiting on Public Endpoints
- **Abuse & Spam Protection**: Public service booking and contact form submissions are rate-limited to 5 submissions per IP address per 10 minutes using Django's cache framework, returning friendly alerts rather than abrupt raw error codes.

#### 7. Dashboard Pagination
- **Scalable Contacts & Bookings Hub**: Paginated the creator's contacts and bookings dashboards at 25 items per page with responsive Next/Previous controls that preserve search filters.

#### 8. Dashboard Views Modularization
- **Clean Architecture**: Decomposed the monolithic `apps/dashboard/views.py` into focused domain modules (`overview.py`, `links.py`, `social.py`, `appearance.py`, `bookings.py`, `contacts.py`, `profile.py`) re-exported via `__init__.py`, preserving full backward compatibility with dashboard URLs.

#### 9. SQLite Concurrency Documentation
- **Database Parity Notes**: Added concurrency documentation regarding SQLite's lack of `select_for_update` row locks, clarifying that MariaDB/MySQL is required for production-level double-booking race condition prevention.

#### 10. Local Typography Backup (Poppins Font)
- **Offline & Cloud Resilience**: Bundled Poppins font files (Regular, Medium, SemiBold, Bold in modern WOFF2 and TTF formats) directly inside `static/fonts/poppins/` with `@font-face` fallbacks, guaranteeing rapid loading and complete resilience if external CDNs are unavailable.

#### 11. Mandatory Email Confirmation Prior to Login
- **Activation Gate**: Users must verify their email before accessing their account. Unverified sign-in attempts are blocked with clear instructions and a one-click resend link.
- **Verification Workflow**: Integrated tokenized verification links with 24-hour expiration (`/auth/confirm-email/<uidb64>/<token>/`), plus a dedicated resend confirmation page.

#### 12. Password Reset Flow Redesign
- **Consistent UI**: Redesigned all four password reset templates (`password_reset.html`, `password_reset_done.html`, `password_reset_confirm.html`, `password_reset_complete.html`) to use Bootstrap 5 cards, brand badges, and responsive layouts matching the main login experience.
- **Custom Plain-Text Email**: Created clean email templates (`password_reset_email.txt`, `password_reset_subject.txt`) dispatched via Brevo SMTP.

#### 13. Full Administrator Access Across Site
- **Unrestricted Admin Privileges**: Lifted the middleware block that previously redirected staff and superusers away from the creator dashboard. Admins can now manage creator pages, appearance, bookings, and links directly, with an integrated "Admin Console" quick link in the dashboard navigation.
- **Automatic Profile Provisioning**: Staff and superuser accounts automatically have creator profiles and appearance settings provisioned.

#### 14. Performance & Load Time Optimization
- **Persistent DB Connections**: Configured `CONN_MAX_AGE = 600` and `CONN_HEALTH_CHECKS = True` to eliminate the latency of establishing new SSL connections to remote MariaDB/SkySQL on every request.
- **Non-Blocking Font Loading**: Made Google Fonts load asynchronously with `media="print" onload="this.media='all'"` while local Poppins renders immediately, preventing render blocking.
- **Removed Render-Blocking `@import`**: Replaced CSS `@import` rules with direct `<link>` tags.
- **Static Asset Caching**: Added `WHITENOISE_MAX_AGE = 31536000` for 1-year browser caching of static files.
- **Query Optimization**: Eliminated redundant database lookups in profile and dashboard overview views.

