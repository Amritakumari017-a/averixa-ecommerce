# Averixa Commerce — Django E-commerce Starter

A responsive full-stack online store built with Django, HTML, CSS, JavaScript, and a database configuration that defaults to SQLite locally and supports PostgreSQL through `DATABASE_URL`.

## Included
- Responsive storefront with search, category filter, sorting, product detail pages
- Session-based cart with quantity updates/removal
- Signup, login, logout, Django password reset flow
- Account page and order history
- Checkout that creates a pending order and never marks it paid just because a browser returned
- Stripe Checkout Session integration when real Stripe secret keys are configured
- Stripe webhook signature verification endpoint
- Customer reviews/ratings with one review per user per product
- Django admin for products, categories, orders, reviews, and users
- Seed command for demo categories/products
- Basic automated tests
- `.env.example`, deployment checklist, and setup docs

## Requirements
Python 3.11+ recommended. Python 3.13 should work with current Django 5.2, but use a supported Python version for your host.

## Local setup (Windows PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```
Open `http://127.0.0.1:8000/`. Admin is at `http://127.0.0.1:8000/admin/`.

## Local setup (macOS/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

## Database
Without `DATABASE_URL`, the app uses SQLite for easiest local setup. For PostgreSQL, set `DATABASE_URL` in `.env` or your host environment, for example:
`postgres://USER:PASSWORD@HOST:5432/DBNAME`

## Payments — important
- Without `STRIPE_SECRET_KEY`, checkout uses a clearly labeled demo/unavailable payment path and does **not** mark orders as paid.
- With a Stripe secret key, the server creates a Stripe Checkout Session. Card data is handled by Stripe, not stored by this app.
- Set `STRIPE_WEBHOOK_SECRET` and configure Stripe to send `checkout.session.completed` events to `/payments/stripe/webhook/`. The webhook verifies the Stripe signature.
- Do not use live keys until you have completed test-mode checks and deployment review.

## Email
If SMTP variables are blank, Django prints email messages to the terminal. Password reset works locally by reading the terminal output. For real users, configure SMTP credentials.

## Tests and checks
```bash
python manage.py check
python manage.py test
python manage.py check --deploy
```
`check --deploy` warnings are expected until production secrets, HTTPS, host, and cookies are configured.

## Known limits / owner action required
See `docs/OWNER_ACTIONS.md` and `storefront/production_checklist.md`. No project ZIP can include your domain, live credentials, hosting account, payment merchant account, shipping provider account, or verified legal policies.
