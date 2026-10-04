# Feature inventory

## Included in source
- [x] Storefront homepage and responsive navigation
- [x] Product catalog and category filtering
- [x] Search by product name, description, and category
- [x] Sort by featured, newest, and price
- [x] Product detail, stock display, image URL, review summary
- [x] Session cart, add/update/remove quantities
- [x] Registration, login/logout, password reset
- [x] Account page and private order history
- [x] Checkout address form and server-side order creation
- [x] Explicit unpaid status if Stripe is not configured
- [x] Stripe Checkout Session creation when keys are configured
- [x] Stripe webhook signature verification and paid-state transition
- [x] Admin CRUD for catalog, categories, orders, reviews, and standard users
- [x] Unique review per user/product and 1–5 rating validation
- [x] SQLite local database; PostgreSQL via DATABASE_URL
- [x] Demo catalog seed command
- [x] Automated Django tests for core paths
- [x] Setup, owner-action, and production checklists

## Deliberately not claimed as finished
- [ ] Custom one-time email verification after signup
- [ ] Wishlist / saved products
- [ ] Coupon / promotion engine
- [ ] Tax engine and configurable shipping zones
- [ ] Live courier integration / GPS tracking
- [ ] Refund workflow with Stripe API reconciliation
- [ ] Product image upload UI (admin can use image URL for starter)
- [ ] Newsletter provider integration
- [ ] Multi-vendor seller portal
- [ ] Automated invoice PDF
- [ ] Social login
- [ ] Product variants (size/color)
- [ ] Real production deployment, domain, backups, and monitoring

These are listed explicitly so they are not mistaken for working features. They can be added in later iterations.
