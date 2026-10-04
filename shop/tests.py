from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Category, Product, Order, Review

class ShopFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            category=self.category, name="Test Product", description="A test product",
            price=Decimal("100.00"), stock=5, is_active=True
        )
        self.user = User.objects.create_user(username="buyer", password="StrongPass123!", email="buyer@example.com")

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Good things.")

    def test_product_search(self):
        response = self.client.get(reverse("product_list"), {"q": "Test Product"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")

    def test_add_to_cart_requires_post(self):
        response = self.client.get(reverse("cart_add", args=[self.product.id]))
        self.assertEqual(response.status_code, 405)

    def test_add_to_cart(self):
        response = self.client.post(reverse("cart_add", args=[self.product.id]), {"quantity": 2})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("cart"))
        self.assertContains(response, "Test Product")
        self.assertContains(response, "200.00")

    def test_checkout_requires_login(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_review_requires_login(self):
        response = self.client.post(reverse("add_review", args=[self.product.slug]), {"rating": 5, "body": "Great"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_review_one_per_user_product(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(reverse("add_review", args=[self.product.slug]), {"rating": 5, "title": "Nice", "body": "Works well"})
        self.client.post(reverse("add_review", args=[self.product.slug]), {"rating": 4, "title": "Again", "body": "Second"})
        self.assertEqual(Review.objects.filter(product=self.product, user=self.user).count(), 1)

    def test_account_page_requires_login(self):
        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 302)

    def test_unconfigured_checkout_never_marks_paid(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(reverse("cart_add", args=[self.product.id]), {"quantity": 1})
        response = self.client.post(reverse("checkout"), {
            "full_name": "Buyer Example", "email": "buyer@example.com", "phone": "",
            "address_line_1": "123 Test Street", "address_line_2": "", "city": "Bengaluru",
            "state": "Karnataka", "postal_code": "560001", "country": "India",
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.payment_status, "unpaid")
        self.assertEqual(order.total, Decimal("179.00"))
        self.assertEqual(self.product.stock, 5)

    def test_order_not_visible_to_other_user(self):
        order = Order.objects.create(
            user=self.user, full_name="Buyer Example", email="buyer@example.com",
            address_line_1="123 Test Street", city="Bengaluru", state="Karnataka",
            postal_code="560001", subtotal=Decimal("100.00"), shipping_fee=Decimal("79.00"),
            total=Decimal("179.00")
        )
        other = User.objects.create_user(username="other", password="StrongPass123!")
        self.client.login(username="other", password="StrongPass123!")
        response = self.client.get(reverse("order_detail", args=[order.order_number]))
        self.assertEqual(response.status_code, 404)
