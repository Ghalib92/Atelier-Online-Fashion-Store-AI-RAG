from django.contrib import admin
from .models import Product, ProductCategory, Order, Wishlist, OrderStatus

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'size', 'color', 'quantity', 'created_at')
    list_filter = ('size', 'color')
    search_fields = ('name', 'color')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'quantity')
    search_fields = ('name', 'category')
    list_filter = ('category',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'details', 'price', 'category', 'quantity')
        }),
        ('Variants', {
            'fields': ('available_sizes', 'available_colors')
        }),
        ('Media', {
            'fields': ('image', 'image_2', 'image_3')
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'total_amount', 'selected_size', 'selected_color', 'paid')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')

@admin.action(description='Mark selected orders as Delivered')
def mark_as_delivered(modeladmin, request, queryset):
    for order in queryset:
        OrderStatus.objects.create(order=order, status='delivered')


