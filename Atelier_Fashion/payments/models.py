from django.db import models
from django.contrib.auth.models import User

class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Pending')
    paid_at = models.DateTimeField(null=True, blank=True)
