from django.shortcuts import render
from .models import Product

# Create your views here.


def home (request):
     products = Product.objects.all().order_by('-created_at')
     return render(request, 'index.html', {'products': products})