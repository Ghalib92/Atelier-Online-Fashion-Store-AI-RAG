from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from .models import Cart, Order, OrderStatus
from .models import ProductCategory  # adjust path

LOW_STOCK_THRESHOLD = getattr(settings, "LOW_STOCK_THRESHOLD", 10)
ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", settings.DEFAULT_FROM_EMAIL)


@receiver(user_logged_in)
def create_user_cart(sender, request, user, **kwargs):
    Cart.objects.get_or_create(user=user)


@receiver(post_save, sender=Order)
def handle_order_paid(sender, instance, **kwargs):
    if instance.paid and not instance.stock_reduced:
        def _reduce_and_notify():
            low_stock_items = []
            for item in instance.items.select_related('product').all():
                product = item.product
                product.quantity = max(product.quantity - item.quantity, 0)
                product.save(update_fields=['quantity'])

                if product.quantity < LOW_STOCK_THRESHOLD:
                    low_stock_items.append(product)

            instance.stock_reduced = True
            instance.save(update_fields=['stock_reduced'])

            if low_stock_items:
                lines = []
                for p in low_stock_items:
                    admin_link = f"{settings.SITE_URL.rstrip('/')}/admin/{p._meta.app_label}/{p._meta.model_name}/{p.id}/change/"
                    lines.append(f"- {p.name} — {p.quantity} left — Manage: {admin_link}")
                send_mail(
                    subject=f"[ALERT] Low stock items ({len(low_stock_items)})",
                    message="\n".join(lines),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ADMIN_EMAIL],
                )

            try:
                send_mail(
                    subject=f"Payment confirmed — Order #{instance.id}",
                    message=f"Hello {instance.full_name}, your payment is confirmed.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
            except Exception:
                pass

        transaction.on_commit(_reduce_and_notify)


@receiver(post_save, sender=OrderStatus)
def send_order_status_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject=f"Order #{instance.order.id} status update",
            message=f"Hello {instance.order.full_name}, your order is now {instance.get_status_display()}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.order.email],
            fail_silently=True,
        )
