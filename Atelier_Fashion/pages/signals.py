from django.contrib.auth.signals import user_logged_in, post_save
from django.dispatch import receiver
from .models import Cart, OrderItem, OrderStatus
from .models import Order
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta





@receiver(user_logged_in)
def create_user_cart(sender, request, user, **kwargs):
    Cart.objects.get_or_create(user=user)


@receiver(post_save, sender=Order)
def handle_order_payment_and_status(sender, instance, created, **kwargs):
    # Reduce stock only when payment is confirmed
    if instance.paid and not hasattr(instance, "_stock_reduced"):
        for item in instance.items.all():
            product = item.product
            product.quantity -= item.quantity
            if product.quantity < 0:
                product.quantity = 0
            product.save()
        instance._stock_reduced = True  # Avoid duplicate runs

    # Send email notification when order is paid
    if instance.paid:
        send_mail(
            subject=f"Order #{instance.id} Payment Confirmed",
            message=f"Hello {instance.full_name},\n\nYour payment for Order #{instance.id} has been confirmed. Estimated delivery: {instance.created_at.date() + timedelta(days=3)}.\n\nThank you for shopping with us!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )

 
# orders/signals.py
@receiver(post_save, sender=OrderStatus)
def send_status_update_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject=f"Order #{instance.order.id} Status Update",
            message=f"Hello {instance.order.full_name},\n\nYour order status is now: {instance.get_status_display()}.\n\nThank you for shopping with us!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.order.email],
            fail_silently=False,
        )
def mark_order_paid(order):
    if not order.paid:
        order.paid = True
        order.save()

        # Reduce stock
        for item in order.items.all():
            product = item.product
            product.quantity -= item.quantity
            product.save()

            # Send low stock email
            if product.quantity < 10:
                send_mail(
                    subject="Low Stock Alert",
                    message=f"Product '{product.name}' stock is low: {product.quantity} items left. Please restock.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],  # set in settings.py
                )