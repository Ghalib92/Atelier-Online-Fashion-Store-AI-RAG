from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cart, CartItem, Order, ProductCategory


def make_product(**kwargs):
    defaults = dict(name="Red Dress", price=2000, category="dresses", color="Red", quantity=20)
    defaults.update(kwargs)
    return ProductCategory.objects.create(**defaults)


class CatalogTests(APITestCase):
    def setUp(self):
        self.product = make_product()

    def test_anyone_can_list_products(self):
        resp = self.client.get(reverse("product-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_non_staff_cannot_create_product(self):
        user = User.objects.create_user("u", password="Str0ngPass!23")
        self.client.force_authenticate(user)
        resp = self.client.post(reverse("product-list"), {"name": "x", "price": 5, "category": "tops"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_product(self):
        admin = User.objects.create_user("a", password="Str0ngPass!23", is_staff=True)
        self.client.force_authenticate(admin)
        resp = self.client.post(
            reverse("product-list"),
            {"name": "Blue Top", "price": 900, "category": "tops", "color": "Blue", "quantity": 5},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_similar_action(self):
        make_product(name="Another Red Dress", color="Red")
        resp = self.client.get(reverse("product-similar", args=[self.product.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)


class CartAndCheckoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("buyer", password="Str0ngPass!23")
        self.product = make_product()
        self.client.force_authenticate(self.user)

    def test_add_item_and_view_cart(self):
        resp = self.client.post(
            reverse("cart-item-list"), {"product_id": self.product.id, "quantity": 2}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cart = self.client.get(reverse("cart")).data
        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(str(cart["total_price"]), "4000.00")

    def test_checkout_cod_creates_order_and_clears_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        resp = self.client.post(
            reverse("checkout"),
            {
                "full_name": "Buyer One", "email": "b@example.com", "phone": "0712345678",
                "address": "123 St", "payment_method": "cod",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        self.assertEqual(cart.items.count(), 0)
        # COD adds a 200 surcharge to the 2000 product
        self.assertEqual(str(resp.data["total_amount"]), "2200.00")

    def test_checkout_empty_cart_rejected(self):
        resp = self.client.post(
            reverse("checkout"),
            {
                "full_name": "X", "email": "b@example.com", "phone": "0712",
                "address": "St", "payment_method": "cod",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class WishlistTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("w", password="Str0ngPass!23")
        self.product = make_product()
        self.client.force_authenticate(self.user)

    def test_toggle_adds_then_removes(self):
        url = reverse("wishlist-toggle", args=[self.product.id])
        self.assertTrue(self.client.post(url).data["in_wishlist"])
        self.assertFalse(self.client.post(url).data["in_wishlist"])


class AnalyticsTests(APITestCase):
    def test_requires_admin(self):
        user = User.objects.create_user("plain", password="Str0ngPass!23")
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get(reverse("analytics")).status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_ok(self):
        admin = User.objects.create_superuser("admin", password="Str0ngPass!23")
        self.client.force_authenticate(admin)
        resp = self.client.get(reverse("analytics"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("totals", resp.data)
