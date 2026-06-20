from django.contrib import admin
from .models import Product, ProductCategory, Order, Wishlist, OrderStatus, OrderItem

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

class OrderItemInline(admin.StackedInline):  # change from TabularInline
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'size', 'color']
    can_delete = False
    show_change_link = False

class OrderStatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, OrderStatusInline]
    list_display = ['id', 'user', 'full_name', 'total_amount', 'latest_status', 'created_at']
    readonly_fields = ['user', 'full_name', 'email', 'phone', 'total_amount', 'created_at']

    def latest_status(self, obj):
        last_status = obj.statuses.last()
        return last_status.get_status_display() if last_status else "No Status"
    latest_status.short_description = "Current Status"

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')

@admin.action(description='Mark selected orders as Delivered')
def mark_as_delivered(modeladmin, request, queryset):
    for order in queryset:
        OrderStatus.objects.create(order=order, status='delivered')


