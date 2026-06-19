import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from pages.models import Order
from .models import PaymentTransaction


class STKPushTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("payer", password="Str0ngPass!23")
        self.order = Order.objects.create(
            user=self.user, full_name="Payer", email="p@example.com", phone="0712",
            address="St", payment_method="mpesa", total_amount=1500, paid=False,
        )
        self.client.force_authenticate(self.user)

    @patch("payments.views.lipa_na_mpesa")
    def test_stk_push_creates_pending_transaction(self, mock_stk):
        mock_stk.return_value = {"CheckoutRequestID": "ws_CO_1", "CustomerMessage": "Sent"}
        resp = self.client.post(
            reverse("stk_push"), {"order_id": self.order.id, "phone": "254712345678"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        txn = PaymentTransaction.objects.get(checkout_request_id="ws_CO_1")
        self.assertEqual(txn.status, "Pending")


class CallbackTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("payer", password="Str0ngPass!23")
        self.order = Order.objects.create(
            user=self.user, full_name="Payer", email="p@example.com", phone="0712",
            address="St", payment_method="mpesa", total_amount=1500, paid=False,
        )
        self.txn = PaymentTransaction.objects.create(
            order=self.order, user=self.user, phone="254712345678",
            amount=1500, checkout_request_id="ws_CO_1", status="Pending",
        )

    def test_successful_callback_marks_order_paid(self):
        payload = {
            "Body": {"stkCallback": {
                "CheckoutRequestID": "ws_CO_1",
                "ResultCode": 0,
                "CallbackMetadata": {"Item": [{"Name": "Amount", "Value": 1500}]},
            }}
        }
        resp = self.client.post(
            reverse("mpesa_callback"), data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.txn.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.txn.status, "Success")
        self.assertTrue(self.order.paid)

    def test_failed_callback_marks_transaction_failed(self):
        payload = {"Body": {"stkCallback": {"CheckoutRequestID": "ws_CO_1", "ResultCode": 1032}}}
        self.client.post(
            reverse("mpesa_callback"), data=json.dumps(payload), content_type="application/json"
        )
        self.txn.refresh_from_db()
        self.assertEqual(self.txn.status, "Failed")
        self.assertFalse(Order.objects.get(id=self.order.id).paid)
