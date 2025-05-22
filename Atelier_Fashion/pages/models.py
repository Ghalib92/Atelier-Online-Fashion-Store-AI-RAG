from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Fashion-related fields
    size_choices = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    size = models.CharField(max_length=2, choices=size_choices, default='M')
    
    color = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    
    # Optional image field for product photos
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def get_availability_display(self):
     if self.quantity > 10:
        return "In Stock"
     elif self.quantity > 0:
        return "Low Stock"
     return "Out of Stock"

    def get_availability_class(self):
     if self.quantity > 10:
        return "in-stock"
     elif self.quantity > 0:
        return "low-stock"
     return "out-of-stock"
    
    def __str__(self):
        return self.name
