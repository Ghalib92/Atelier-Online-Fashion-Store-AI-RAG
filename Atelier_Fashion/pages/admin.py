from django.contrib import admin
from .models import Product, ProductCategory, OrderStatus

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'size', 'color', 'quantity', 'created_at')
    list_filter = ('size', 'color')
    search_fields = ('name', 'color')


@admin.register(ProductCategory)
class ProductCategory(admin.ModelAdmin):
    list_display = ('name', 'price', 'size', 'color', 'quantity','category','created_at')
    list_filter = ('size', 'color')
    search_fields = ('name', 'color')


@admin.action(description='Mark selected orders as Delivered')
def mark_as_delivered(modeladmin, request, queryset):
    for order in queryset:
        OrderStatus.objects.create(order=order, status='delivered')


