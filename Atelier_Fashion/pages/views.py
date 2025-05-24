from django.shortcuts import render
from .models import Product,ProductCategory

# Create your views here.


def home (request):
     products = Product.objects.all().order_by('-created_at')
     return render(request, 'index.html', {'products': products})


def graduation(request):
     products = ProductCategory.objects.filter(category = 'graduation')
     return render(request,'graduation.html', {'products': products})

