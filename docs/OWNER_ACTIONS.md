# Owner actions required before launch

These cannot safely be completed inside a source-code ZIP:

1. Create a Stripe account and configure test keys. Configure a webhook pointing to `/payments/stripe/webhook/`; only switch to live keys after full test-mode verification.
2. Choose and configure email/SMTP provider. Verify account emails and password reset.
3. Provision PostgreSQL for production and configure `DATABASE_URL`.
4. Buy/configure a domain, deploy to a Python-compatible host, enable HTTPS, configure environment variables and static/media storage.
5. Add real product photography, inventory, prices, shipping zones, tax settings, refund/return policy, privacy policy, terms, and support details.
6. Decide whether email verification is mandatory. This starter includes password reset and Django's standard authentication, but not a custom one-time email verification flow.
7. If you need courier tracking, connect a real carrier API. The included order status is admin-updated, not live courier GPS tracking.
8. Review legal, security, accessibility, performance, and privacy requirements before handling real customers.
