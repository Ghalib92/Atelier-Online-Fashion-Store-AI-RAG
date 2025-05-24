from django.shortcuts import render,get_object_or_404
from .models import Product,ProductCategory

# Create your views here.


def home (request):
     products = ProductCategory.objects.all().order_by('-created_at')
     return render(request, 'index.html', {'products': products})



def category_view(request, category_name):
    products = ProductCategory.objects.filter(category=category_name)
    return render(request, 'products.html', {
        'products': products,
        'category': category_name.replace('_', ' ').title()  # For display
    })

def product_detail(request, id):
    product = get_object_or_404(ProductCategory, id=id)  # using 'id' instead of 'pk'
    return render(request, 'product_details.html', {'product': product})