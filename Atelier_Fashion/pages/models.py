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


class ProductCategory (models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField(blank=True, null=True)
    available_sizes = models.CharField(
        max_length=255, help_text="Enter sizes comma-separated, e.g. S,M,L,XL",
        blank=True, null=True
    )
    available_colors = models.CharField(
        max_length=255, help_text="Enter colors comma-separated, e.g. Red,Blue,Green",
        blank=True, null=True
    )
   
    
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

    category_options = [
       
      ('dresses','Dresses'),
      ('pants_sets','Pants Sets'),
      ('skirts','Skirts'),
      ('tops','Tops'),
      
    ]
    category = models.CharField( choices=category_options, default= 'occassion')
    # Optional image field for product photos
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True)
    

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_sizes(self):
        if not self.available_sizes:
            return []
        return [size.strip() for size in self.available_sizes.split(',') if size.strip()]

    def get_colors(self):
        if not self.available_colors:
            return []
        return [color.strip() for color in self.available_colors.split(',') if color.strip()]

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



 
from django.contrib.auth.models import User
 

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
     
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s cart"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

from django.utils import timezone  
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(default=timezone.now)
    size = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)


    
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.size}/{self.color})"


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('cod', 'Cash on Delivery'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    selected_size = models.CharField(max_length=10, blank=True, null=True)
    selected_color = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderStatus(models.Model):
    STATUS_CHOICES = [
        ('received', 'Order Received & Processing'),
        ('delivering', 'Delivering Today'),
        ('delivered', 'Delivered'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.get_status_display()}"



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"

