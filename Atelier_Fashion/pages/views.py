from django.shortcuts import render,get_object_or_404, redirect
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


from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, ProductCategory 

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(ProductCategory, id=product_id)
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If item already exists in cart, increase quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')  # Name of the cart page URL
@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'cart.html', {'cart': cart})
