from django.db import models
from django.contrib.auth.models import User
from pages.models import Order

class PaymentTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Pending')
    paid_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} - {self.amount} [{self.status}]"
