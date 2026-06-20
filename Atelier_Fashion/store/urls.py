from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalyticsView,
    CartItemViewSet,
    CartView,
    CheckoutView,
    OrderViewSet,
    ProductCategoryViewSet,
    ProductViewSet,
    WishlistViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductCategoryViewSet, basename="product")
router.register(r"catalog-items", ProductViewSet, basename="catalog-item")
router.register(r"cart/items", CartItemViewSet, basename="cart-item")
router.register(r"wishlist", WishlistViewSet, basename="wishlist")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
    path("", include(router.urls)),
]
