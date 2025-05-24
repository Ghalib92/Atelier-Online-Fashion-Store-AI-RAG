from django.shortcuts import render
from .models import Product,ProductCategory

# Create your views here.


def home (request):
     products = Product.objects.all().order_by('-created_at')
     return render(request, 'index.html', {'products': products})



def category_view(request, category_name):
    products = ProductCategory.objects.filter(category=category_name)
    return render(request, 'products.html', {
        'products': products,
        'category': category_name.replace('_', ' ').title()  # For display
    })

