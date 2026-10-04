import json
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .cart import add_to_cart, clear_cart, get_cart_items, update_cart
from .forms import SignupForm, CheckoutForm, ReviewForm
from .models import Category, Product, Order, OrderItem, Review

def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:8]
    if not featured:
        featured = Product.objects.filter(is_active=True).select_related("category")[:8]
    categories = Category.objects.filter(is_active=True)[:8]
    latest = Product.objects.filter(is_active=True).select_related("category")[:8]
    return render(request, "shop/home.html", {"featured": featured, "categories": categories, "latest": latest})

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q", "").strip()[:100]
    category_slug = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "featured")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    else:
        products = products.order_by("-is_featured", "-created_at")
    return render(request, "shop/product_list.html", {
        "products": products, "categories": Category.objects.filter(is_active=True),
        "query": query, "selected_category": category_slug, "selected_sort": sort,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    reviews = product.reviews.select_related("user")[:10]
    review_form = ReviewForm()
    return render(request, "shop/product_detail.html", {"product": product, "reviews": reviews, "review_form": review_form})

def cart_view(request):
    items, total = get_cart_items(request)
    return render(request, "shop/cart.html", {"items": items, "total": total})

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 1
    if product.stock < 1:
        messages.error(request, "This product is currently out of stock.")
    else:
        add_to_cart(request, product, min(quantity, product.stock))
        messages.success(request, f"{product.name} added to your cart.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect("cart")

@require_POST
def cart_update(request, product_id):
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 1
    if quantity > 0:
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        quantity = min(quantity, product.stock, 99)
    update_cart(request, product_id, quantity)
    messages.success(request, "Cart updated.")
    return redirect("cart")

@login_required
def checkout(request):
    items, subtotal = get_cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("product_list")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Recheck stock at order creation. Payment confirmation is separate.
            for item in items:
                item["product"].refresh_from_db()
                if item["quantity"] > item["product"].stock:
                    messages.error(request, f"Not enough stock for {item['product'].name}. Please update your cart.")
                    return redirect("cart")
            shipping_fee = Decimal("0.00") if subtotal >= Decimal("999.00") else Decimal("79.00")
            total = subtotal + shipping_fee
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user, subtotal=subtotal, shipping_fee=shipping_fee, total=total,
                    **form.cleaned_data,
                )
                for item in items:
                    product = Product.objects.select_for_update().get(pk=item["product"].pk)
                    if product.stock < item["quantity"]:
                        messages.error(request, f"Stock changed for {product.name}. Please try again.")
                        return redirect("cart")
                    OrderItem.objects.create(
                        order=order, product=product, product_name=product.name,
                        unit_price=product.price, quantity=item["quantity"],
                        line_total=product.price * item["quantity"],
                    )
            if settings.STRIPE_SECRET_KEY:
                try:
                    import stripe
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    session = stripe.checkout.Session.create(
                        mode="payment",
                        customer_email=order.email,
                        client_reference_id=str(order.pk),
                        metadata={"order_id": str(order.pk), "order_number": order.order_number},
                        line_items=[{
                            "price_data": {
                                "currency": "inr",
                                "product_data": {"name": line.product_name},
                                "unit_amount": int(line.unit_price * 100),
                            },
                            "quantity": line.quantity,
                        } for line in order.items.all()] + ([{
                            "price_data": {"currency": "inr", "product_data": {"name": "Shipping"}, "unit_amount": int(order.shipping_fee * 100)},
                            "quantity": 1,
                        }] if order.shipping_fee else []),
                        success_url=request.build_absolute_uri(reverse("order_detail", args=[order.order_number])) + "?payment=pending",
                        cancel_url=request.build_absolute_uri(reverse("order_detail", args=[order.order_number])) + "?payment=cancelled",
                    )
                    order.stripe_session_id = session.id
                    order.save(update_fields=["stripe_session_id", "updated_at"])
                    clear_cart(request)
                    return redirect(session.url, permanent=False)
                except Exception:
                    order.status = "pending"
                    order.save(update_fields=["status", "updated_at"])
                    messages.error(request, "Payment could not be started. The order is still unpaid; contact support or retry after configuration.")
                    return redirect("order_detail", order_number=order.order_number)
            clear_cart(request)
            messages.warning(request, "Payment is not configured yet. This order is saved as UNPAID; no payment was taken.")
            return redirect("order_detail", order_number=order.order_number)
    else:
        form = CheckoutForm(initial={"full_name": request.user.get_full_name(), "email": request.user.email})
    return render(request, "shop/checkout.html", {"items": items, "subtotal": subtotal, "form": form})

@login_required
def account(request):
    orders = request.user.shop_orders.all()[:20]
    return render(request, "shop/account.html", {"orders": orders})

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    return render(request, "shop/order_detail.html", {"order": order})

@login_required
@require_POST
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = ReviewForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct the review form.")
        return redirect(product.get_absolute_url())
    review, created = Review.objects.get_or_create(
        product=product, user=request.user,
        defaults={"rating": form.cleaned_data["rating"], "title": form.cleaned_data["title"], "body": form.cleaned_data["body"]},
    )
    if not created:
        messages.info(request, "You have already reviewed this product.")
    else:
        messages.success(request, "Review submitted.")
    return redirect(product.get_absolute_url())

def signup(request):
    if request.user.is_authenticated:
        return redirect("account")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data.get("first_name", "")
            user.last_name = form.cleaned_data.get("last_name", "")
            user.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("account")
    else:
        form = SignupForm()
    return render(request, "shop/signup.html", {"form": form})

def stripe_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    if not settings.STRIPE_WEBHOOK_SECRET or not settings.STRIPE_SECRET_KEY:
        return HttpResponseForbidden("Stripe webhook is not configured.")
    try:
        import stripe
        event = stripe.Webhook.construct_event(
            request.body, request.headers.get("Stripe-Signature", ""), settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponseBadRequest("Invalid Stripe webhook signature or payload.")
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        if order_id:
            try:
                with transaction.atomic():
                    order = Order.objects.select_for_update().get(pk=int(order_id))
                    if order.stripe_session_id == session.get("id") and session.get("payment_status") == "paid" and order.payment_status != "paid":
                        # Idempotent transition: inventory is decremented only on first paid transition.
                        order.payment_status = "paid"
                        order.status = "processing"
                        order.save(update_fields=["payment_status", "status", "updated_at"])
                        for line in order.items.select_related("product"):
                            product = Product.objects.select_for_update().get(pk=line.product_id)
                            if product.stock >= line.quantity:
                                product.stock -= line.quantity
                                product.save(update_fields=["stock", "updated_at"])
                            else:
                                # Avoid negative stock; alert through logs/monitoring in a real deployment.
                                import logging
                                logging.getLogger(__name__).error("Paid order %s exceeds stock for product %s", order.order_number, product.pk)
            except (Order.DoesNotExist, ValueError):
                pass
    return HttpResponse(status=200)

def about(request):
    return render(request, "shop/static_page.html", {"page_title": "About Averixa", "page_text": "A thoughtfully designed online shopping experience. Replace this copy with your real business story before launch."})

def contact(request):
    return render(request, "shop/static_page.html", {"page_title": "Contact", "page_text": "Add your real support email, phone, and business address before launch."})
