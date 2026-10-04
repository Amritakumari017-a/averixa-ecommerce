# Production deployment checklist

This project is a functional starter, not a certified production deployment. Before public launch:

- [ ] Set a strong random `SECRET_KEY` in the hosting environment.
- [ ] Set `DEBUG=False`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.
- [ ] Configure managed PostgreSQL and backups.
- [ ] Configure SMTP email delivery and verify password-reset delivery.
- [ ] Configure Stripe test keys first, then live keys only after testing.
- [ ] Add a Stripe webhook endpoint and verify event signatures before relying on async payment updates.
- [ ] Configure HTTPS, domain, static file serving, media storage, and monitoring.
- [ ] Add shipping/tax rules, refund policy, privacy policy, terms, support contact, and legal/business details.
- [ ] Review rate limiting, bot protection, logging, and error monitoring.
- [ ] Run `python manage.py check --deploy` and fix all warnings.
- [ ] Test checkout with real Stripe test cards in Stripe's test mode.
- [ ] Do not accept or store raw card numbers in this application.
