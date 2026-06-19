from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def test_register_then_login(self):
        resp = self.client.post(
            reverse("register"),
            {"username": "shopper", "password": "Str0ngPass!23", "email": "s@example.com"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", resp.data)

        resp = self.client.post(
            reverse("login"), {"username": "shopper", "password": "Str0ngPass!23"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_weak_password_rejected(self):
        resp = self.client.post(reverse("register"), {"username": "x", "password": "1"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_requires_auth(self):
        self.assertEqual(
            self.client.get(reverse("profile")).status_code, status.HTTP_401_UNAUTHORIZED
        )
