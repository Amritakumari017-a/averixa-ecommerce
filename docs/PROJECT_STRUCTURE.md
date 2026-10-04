# Project structure

- `storefront/settings.py` — environment settings, database, email, security
- `storefront/urls.py` — admin, authentication, password reset, shop routes
- `shop/models.py` — Category, Product, Order, OrderItem, Review
- `shop/views.py` — storefront, cart, checkout, account, reviews, Stripe webhook
- `shop/cart.py` — session cart helpers
- `shop/forms.py` — signup, checkout, review forms
- `shop/admin.py` — admin CRUD and order management
- `shop/migrations/0001_initial.py` — initial database schema
- `shop/management/commands/seed_demo.py` — illustrative sample products
- `shop/templates/shop/` — server-rendered pages
- `shop/static/shop/css/style.css` — responsive styling
- `shop/static/shop/js/app.js` — mobile navigation and small interactions
- `docs/FEATURE_MATRIX.md` — included vs intentionally not included
- `docs/OWNER_ACTIONS.md` — services and setup the owner must complete
- `storefront/production_checklist.md` — launch hardening checklist
