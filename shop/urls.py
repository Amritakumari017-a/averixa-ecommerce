from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("payments/stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("account/", views.account, name="account"),
    path("orders/<str:order_number>/", views.order_detail, name="order_detail"),
    path("products/<slug:slug>/review/", views.add_review, name="add_review"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("signup/", views.signup, name="signup"),
]
