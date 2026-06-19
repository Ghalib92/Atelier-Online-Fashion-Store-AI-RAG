from rest_framework import serializers

from .models import PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = (
            "id", "order", "phone", "amount", "checkout_request_id",
            "status", "paid_at",
        )
        read_only_fields = fields


class STKPushSerializer(serializers.Serializer):
    """Initiate an M-Pesa STK push for one of the user's orders."""

    order_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=15)
