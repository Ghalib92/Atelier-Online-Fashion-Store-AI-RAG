import json

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from pages.models import Cart, Order
from .models import PaymentTransaction
from .mpesa import lipa_na_mpesa
from .serializers import PaymentTransactionSerializer, STKPushSerializer


class STKPushView(APIView):
    """Trigger an M-Pesa STK push prompt for an unpaid order."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=STKPushSerializer, responses={200: OpenApiResponse(description="STK push result.")})
    def post(self, request):
        serializer = STKPushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(
            Order, id=serializer.validated_data["order_id"], user=request.user
        )
        phone = serializer.validated_data["phone"]
        amount = int(order.total_amount)

        result = lipa_na_mpesa(phone, amount, request.user.username)

        PaymentTransaction.objects.create(
            order=order,
            user=request.user,
            phone=phone,
            amount=order.total_amount,
            checkout_request_id=result.get("CheckoutRequestID", ""),
            status="Pending",
        )
        return Response(
            {"detail": result.get("CustomerMessage", "Payment initiated."), "raw": result}
        )


class MpesaCallbackView(APIView):
    """
    Safaricom Daraja callback webhook. Public (no auth) but only acts on a
    matching pending transaction. Marks the order paid on success.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Acknowledged.")})
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return Response({"ResultCode": 1, "ResultDesc": "Invalid payload"})

        stk = data.get("Body", {}).get("stkCallback", {})
        checkout_id = stk.get("CheckoutRequestID")
        result_code = stk.get("ResultCode")
        metadata = {
            item.get("Name"): item.get("Value")
            for item in stk.get("CallbackMetadata", {}).get("Item", [])
        }
        amount_paid = metadata.get("Amount", 0)

        try:
            txn = PaymentTransaction.objects.get(checkout_request_id=checkout_id)
        except PaymentTransaction.DoesNotExist:
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        if result_code == 0 and int(amount_paid or 0) == int(txn.amount):
            txn.status = "Success"
            txn.paid_at = timezone.now()
            txn.save()
            if txn.order:
                txn.order.paid = True
                txn.order.save()  # triggers stock reduction + confirmation email
            cart = Cart.objects.filter(user=txn.user).first()
            if cart:
                cart.items.all().delete()
        else:
            txn.status = "Failed"
            txn.save()

        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


class TransactionListView(generics.ListAPIView):
    """List the authenticated user's payment transactions."""

    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by("-id")
