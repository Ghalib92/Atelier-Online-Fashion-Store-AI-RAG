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


 # orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderStatus
from products.models import ProductCategory  # adjust import to your product model path

LOW_STOCK_THRESHOLD = getattr(settings, "LOW_STOCK_THRESHOLD", 10)
ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", settings.DEFAULT_FROM_EMAIL)

@receiver(post_save, sender=Order)
def handle_order_paid(sender, instance: Order, created, **kwargs):
    """
    When an Order is saved and paid==True and stock_reduced==False:
    - reduce product quantities
    - mark order.stock_reduced = True and save
    - send admin low-stock email for each product below threshold
    - send payment confirmation email to customer (if desired)
    """
    # Only act if order is paid and we haven't reduced stock yet
    if instance.paid and not instance.stock_reduced:
        # Use transaction.on_commit to ensure DB is consistent before sending emails
        def _reduce_and_notify():
            low_stock_items = []
            for item in instance.items.select_related('product').all():
                product = item.product
                # subtract
                product.quantity = max(product.quantity - item.quantity, 0)
                product.save(update_fields=['quantity'])
                if product.quantity < LOW_STOCK_THRESHOLD:
                    low_stock_items.append(product)

            # mark order so we don't do this again
            instance.stock_reduced = True
            instance.save(update_fields=['stock_reduced'])

            # Email admin if low-stock items found
            if low_stock_items:
                lines = []
                for p in low_stock_items:
                    admin_link = f"{settings.SITE_URL.rstrip('/')}/admin/{p._meta.app_label}/{p._meta.model_name}/{p.id}/change/"
                    lines.append(f"- {p.name} — {p.quantity} left — Manage: {admin_link}")
                msg = "Low Stock Alert\n\nThe following products are below the low-stock threshold:\n\n"
                msg += "\n".join(lines)
                send_mail(
                    subject=f"[ALERT] Low stock items ({len(low_stock_items)})",
                    message=msg,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ADMIN_EMAIL],
                    fail_silently=False,
                )

            # Optionally send payment confirmation to customer
            try:
                send_mail(
                    subject=f"Payment confirmed — Order #{instance.id}",
                    message=(
                        f"Hello {instance.full_name},\n\n"
                        f"Your payment for Order #{instance.id} has been confirmed. "
                        f"Estimated delivery: {instance.estimated_delivery_date().date()}.\n\n"
                        "Thank you for shopping with us."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,  # don't crash if mail fails
                )
            except Exception:
                pass

        transaction.on_commit(_reduce_and_notify)


@receiver(post_save, sender=OrderStatus)
def send_order_status_email(sender, instance: OrderStatus, created, **kwargs):
    """
    When a new OrderStatus is created send an email to the customer
    """
    if created:
        subject = f"Order #{instance.order.id} status update"
        message = (
            f"Hello {instance.order.full_name},\n\n"
            f"Your order status is now: {instance.get_status_display()}.\n\n"
            "Thank you."
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.order.email],
            fail_silently=True,
        )
