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
from .models import ProductCategory

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(ProductCategory, id=product_id)
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        return JsonResponse({'success': False, 'error': 'Quantity must be at least 1'})
    
    price = Decimal(str(product.price))
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
        cart[str(product_id)]['total'] = str(price * cart[str(product_id)]['quantity'])
    else:
        cart[str(product_id)] = {
            'title': product.name,
            'price': str(price),
            'quantity': quantity,
            'total': str(price * quantity),
            'image': product.image.url if product.image else ''
        }
    
    request.session['cart'] = cart
    request.session['cart_count'] = sum(item['quantity'] for item in cart.values())
    return JsonResponse({
        'success': True,
        'cart_count': request.session['cart_count'],
        'message': 'Item added to cart!'
    })

def cart_detail(request):
    cart = request.session.get('cart', {})
    total = sum(Decimal(item['total']) for item in cart.values())
    return render(request, 'cart.html', {
        'cart': cart,
        'total': total,
        'cart_count': request.session.get('cart_count', 0)
    })