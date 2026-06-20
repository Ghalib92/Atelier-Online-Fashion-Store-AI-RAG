from rest_framework import serializers

from .models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductCategory,
    Wishlist,
)


class ProductSerializer(serializers.ModelSerializer):
    availability = serializers.CharField(source="get_availability_display", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "description", "price", "size", "color",
            "quantity", "image", "availability", "created_at", "updated_at",
        )


class ProductCategorySerializer(serializers.ModelSerializer):
    """The main catalog item (a sellable product belonging to a category)."""

    availability = serializers.CharField(source="get_availability_display", read_only=True)
    sizes = serializers.ListField(source="get_sizes", child=serializers.CharField(), read_only=True)
    colors = serializers.ListField(source="get_colors", child=serializers.CharField(), read_only=True)

    class Meta:
        model = ProductCategory
        fields = (
            "id", "name", "description", "details", "price", "category",
            "size", "color", "quantity", "available_sizes", "available_colors",
            "sizes", "colors", "image", "image_2", "image_3",
            "availability", "created_at", "updated_at",
        )


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCategorySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), source="product", write_only=True
    )
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_id", "quantity", "size", "color", "total_price", "added_at")
        read_only_fields = ("id", "added_at")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "items", "total_price", "created_at", "updated_at")


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductCategorySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ("id", "product", "product_id", "added_at")
        read_only_fields = ("id", "added_at")


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductCategorySerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "size", "color", "total_price")


class OrderStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = OrderStatus
        fields = ("id", "status", "status_display", "timestamp")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    statuses = OrderStatusSerializer(many=True, read_only=True)
    current_status = serializers.SerializerMethodField()
    estimated_delivery = serializers.DateTimeField(source="estimated_delivery_date", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "full_name", "email", "phone", "address", "payment_method",
            "total_amount", "paid", "items", "statuses", "current_status",
            "estimated_delivery", "created_at",
        )
        read_only_fields = ("id", "total_amount", "paid", "created_at")

    def get_current_status(self, obj):
        last = obj.statuses.last()
        return last.status if last else "received"


class CheckoutSerializer(serializers.Serializer):
    """Create an order from the authenticated user's cart."""

    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES)
