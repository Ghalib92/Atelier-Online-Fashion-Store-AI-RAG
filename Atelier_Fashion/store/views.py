from datetime import timedelta

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Product,
    ProductCategory,
    Wishlist,
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    CheckoutSerializer,
    OrderSerializer,
    ProductCategorySerializer,
    ProductSerializer,
    WishlistSerializer,
)

COD_SURCHARGE = 200


# --------------------------------------------------------------------------- #
# Catalog
# --------------------------------------------------------------------------- #
class ProductViewSet(viewsets.ModelViewSet):
    """Simple standalone products. Read for all, write for staff."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["size", "color"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    Main catalog: products grouped by category (dresses, tops, ...).

    Read access is public; create/update/delete is staff-only. Supports
    filtering by category/size/color, full-text search and ordering.
    """

    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["category", "size", "color"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    @extend_schema(responses={200: ProductCategorySerializer(many=True)})
    @action(detail=True, methods=["get"])
    def similar(self, request, pk=None):
        """Products in the same category sharing a size or colour."""
        product = self.get_object()
        similar = (
            ProductCategory.objects.filter(category=product.category)
            .exclude(id=product.id)
            .filter(Q(color__iexact=product.color) | Q(size=product.size))[:8]
        )
        return Response(self.get_serializer(similar, many=True).data)


# --------------------------------------------------------------------------- #
# Cart
# --------------------------------------------------------------------------- #
class CartView(RetrieveAPIView):
    """Return the authenticated user's cart (created on first access)."""

    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemViewSet(viewsets.ModelViewSet):
    """Add, update quantity for, or remove items from the user's cart."""

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related("product")

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=serializer.validated_data.get("size"),
            color=serializer.validated_data.get("color"),
        )
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        serializer.instance = item


# --------------------------------------------------------------------------- #
# Wishlist
# --------------------------------------------------------------------------- #
class WishlistViewSet(viewsets.ModelViewSet):
    """The authenticated user's wishlist."""

    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related("product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Toggled.")})
    @action(detail=False, methods=["post"], url_path="toggle/(?P<product_id>[^/.]+)")
    def toggle(self, request, product_id=None):
        """Add the product to the wishlist, or remove it if already present."""
        item = Wishlist.objects.filter(user=request.user, product_id=product_id).first()
        if item:
            item.delete()
            return Response({"in_wishlist": False})
        Wishlist.objects.create(user=request.user, product_id=product_id)
        return Response({"in_wishlist": True}, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------- #
# Orders & checkout
# --------------------------------------------------------------------------- #
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve the authenticated user's orders."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product", "statuses")
            .order_by("-created_at")
        )

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Order cancelled.")})
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an order, only allowed before delivery has started."""
        order = self.get_object()
        last = order.statuses.last()
        if last is None or last.status == "received":
            order.delete()
            return Response({"detail": "Order cancelled."})
        return Response(
            {"detail": "You can only cancel before delivery starts."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CheckoutView(APIView):
    """Create an order from the user's cart (Cash on Delivery or M-Pesa)."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=CheckoutSerializer, responses={201: OrderSerializer})
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total = cart.total_price
        if data["payment_method"] == "cod":
            total += COD_SURCHARGE

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                address=data["address"],
                payment_method=data["payment_method"],
                total_amount=total,
                paid=False,
            )
            for item in cart.items.select_related("product").all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    size=item.size,
                    color=item.color,
                )
            if data["payment_method"] == "cod":
                cart.items.all().delete()

        if data["payment_method"] == "cod":
            send_mail(
                "Order Confirmation",
                f"Thank you {data['full_name']}, your order #{order.id} has been received.\n"
                f"Delivery to: {data['address']}\nAmount: Ksh.{total}",
                settings.DEFAULT_FROM_EMAIL,
                [data["email"]],
                fail_silently=True,
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------- #
# Analytics (admin only)
# --------------------------------------------------------------------------- #
class AnalyticsView(APIView):
    """Store-wide sales and inventory metrics. Staff only."""

    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses={200: OpenApiResponse(description="Store metrics.")})
    def get(self, request):
        total_orders = Order.objects.count()
        paid_orders = Order.objects.filter(paid=True).count()
        revenue = Order.objects.filter(paid=True).aggregate(t=Sum("total_amount"))["t"] or 0

        top_products = list(
            ProductCategory.objects.annotate(sold=Sum("orderitem__quantity"))
            .filter(sold__gt=0)
            .order_by("-sold")[:10]
            .values("id", "name", "sold")
        )

        days = int(request.query_params.get("period", 30))
        start = timezone.now().date() - timedelta(days=days - 1)
        sales = (
            Order.objects.filter(paid=True, created_at__date__gte=start)
            .values("created_at__date")
            .annotate(total=Sum("total_amount"))
            .order_by("created_at__date")
        )

        return Response({
            "totals": {
                "users": User.objects.count(),
                "products": ProductCategory.objects.count(),
                "orders": total_orders,
                "paid_orders": paid_orders,
                "unpaid_orders": total_orders - paid_orders,
                "revenue": revenue,
            },
            "low_stock_products": list(
                ProductCategory.objects.filter(quantity__lt=settings.LOW_STOCK_THRESHOLD)
                .values("id", "name", "quantity")
            ),
            "top_products": top_products,
            "sales_trend": [
                {"date": row["created_at__date"].isoformat(), "total": float(row["total"] or 0)}
                for row in sales
            ],
            "period_days": days,
        })
