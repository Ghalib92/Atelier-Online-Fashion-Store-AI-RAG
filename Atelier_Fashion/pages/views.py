from django.shortcuts import render,get_object_or_404, redirect
from .models import Product,ProductCategory

# Create your views here.


def home (request):
     products = ProductCategory.objects.all().order_by('-created_at')
     latest = ProductCategory.objects.all().order_by('-created_at')[:8]


     return render(request, 'index.html', {'products': products, 'latest': latest})



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
from django.db.models import Sum

@login_required
def add_to_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(ProductCategory, id=product_id)
    quantity = int(request.GET.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0

    return JsonResponse({'success': True, 'cart_count': cart_count})
@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'cart.html', {'cart': cart})


from django.views.decorators.http import require_POST
from django.http import JsonResponse

@require_POST
def update_cart_quantity(request):
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')

    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        if action == 'increment':
            item.quantity += 1
        elif action == 'decrement':
            if item.quantity > 1:
                item.quantity -= 1
        item.save()

        cart = item.cart
        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({
            'success': True,
            'quantity': item.quantity,
            'item_total': item.total_price,
            'cart_total': cart.total_price,
            'cart_count': cart_count,
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False}, status=404)



@require_POST
def remove_cart_item(request):
    item_id = request.POST.get('item_id')
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.delete()
        cart = item.cart
        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_price,
            'cart_count': cart_count,
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False}, status=404)



 
from django.shortcuts import render
from django.db.models import Q
 

def product_search(request):
    query = request.GET.get('q', '').strip()
    results = ProductCategory.objects.none()
    
    if query:
        results = ProductCategory.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'search_results.html', {
        'query': query,
        'results': results
    })
