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
       ('work_wear','Work wear'),
        ('graduation','Graduation'),
        ('party', 'Party'),
        ('mini_dresses', 'Mini Dress'),
        ('maxi_dress', 'Maxi Dress'),
        ('knee_lenth_dress', 'Knee Length Dress'),
        ('crop_tops','Crop Tops'),
        ('bodysuits','BodySuits'),
        ('blouses','Blouses'),
        ('wrap_tops','Wrap Tops'),
        ('corsets','Corsets'),
        ('pants','Pants'),
        ('pants_sets','Pants Sets'),
        ('shorts', 'Shorts'),
        ('jackets', 'Jackets'),
        ('kimonos','Kimonos'),
        ('shawls','Shawls'),
        ('Cardigans','Cardigans'),
        ('jewelry','Jewelry'),
        ('belts','Belts'),
        ('sandals','Sandals')







    ]
    category = models.CharField( choices=category_options, default= 'occassion')
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
