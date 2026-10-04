from decimal import Decimal
from .models import Product

CART_SESSION_KEY = "cart"

def _cart(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    return cart if isinstance(cart, dict) else {}

def get_cart_count(request):
    return sum(max(0, int(qty)) for qty in _cart(request).values() if str(qty).isdigit())

def get_cart_items(request):
    cart = _cart(request)
    ids = [int(pk) for pk in cart if str(pk).isdigit()]
    products = Product.objects.filter(id__in=ids, is_active=True).select_related("category")
    items, total = [], Decimal("0.00")
    for product in products:
        try:
            qty = max(1, min(99, int(cart.get(str(product.id), 1))))
        except (ValueError, TypeError):
            qty = 1
        line_total = product.price * qty
        items.append({"product": product, "quantity": qty, "line_total": line_total})
        total += line_total
    return items, total

def add_to_cart(request, product, quantity=1):
    cart = _cart(request).copy()
    key = str(product.id)
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 1
    quantity = max(1, min(99, quantity))
    cart[key] = min(99, int(cart.get(key, 0)) + quantity)
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True

def update_cart(request, product_id, quantity):
    cart = _cart(request).copy()
    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    elif key in cart:
        cart[key] = min(99, quantity)
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True

def clear_cart(request):
    request.session.pop(CART_SESSION_KEY, None)
    request.session.modified = True
