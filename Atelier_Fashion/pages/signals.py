from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart

@receiver(user_logged_in)
def create_user_cart(sender, request, user, **kwargs):
    Cart.objects.get_or_create(user=user)
