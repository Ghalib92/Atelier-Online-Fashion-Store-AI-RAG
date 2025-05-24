from django.contrib import admin
from .models import Product, ProductCategory

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
