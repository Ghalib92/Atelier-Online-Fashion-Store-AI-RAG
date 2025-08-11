from django.shortcuts import render,get_object_or_404, redirect
from .models import Product, ProductCategory, Wishlist, Order, Cart, CartItem, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test


# Create your views here.


def home (request):
     products = ProductCategory.objects.all().order_by('-created_at')
     latest = ProductCategory.objects.all().order_by('-created_at')[:8]



     return render(request, 'index.html', {'products': products, 'latest': latest})



def category_view(request, category_name):
    products = ProductCategory.objects.filter(category=category_name)

    # Filters
    size = request.GET.get('size', '').strip()
    color = request.GET.get('color', '').strip()
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    sort = request.GET.get('sort', '').strip()

    if size:
        products = products.filter(size=size)
    if color:
        products = products.filter(color__iexact=color)
    if price_min and price_min.isdigit():
        products = products.filter(price__gte=price_min)
    if price_max and price_max.isdigit():
        products = products.filter(price__lte=price_max)

    # Safe sorting options
    sort_options = {
        'price_desc': '-price',
        'price_asc': 'price',
        'latest': '-created_at',
        'oldest': 'created_at',
    }
    if sort in sort_options:
        products = products.order_by(sort_options[sort])

    return render(request, 'products.html', {
        'products': products,
        'category': category_name.replace('_', ' ').title(),
        'selected_size': size,
        'selected_color': color,
        'price_min': price_min,
        'price_max': price_max,
        'selected_sort': sort,
    })



def product_detail(request, id):
    product = get_object_or_404(ProductCategory, id=id)

    # Suggest similar products
    recommendations = ProductCategory.objects.filter(
        category=product.category
    ).exclude(id=product.id)

    # Filter similar ones by color or size
    similar_products = recommendations.filter(
    Q(color__iexact=product.color) |
    Q(size=product.size)
    )[:8]
  # limit to 4 suggestions
  # Wishlist check
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'product_details.html', {
        'product': product,
        'similar_products': similar_products,
        'is_favorited': is_favorited
    })


from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, ProductCategory 
from django.db.models import Sum
import json

 





@login_required
@require_POST
def add_to_cart(request, product_id):
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        size = data.get('size')
        color = data.get('color')

        product = get_object_or_404(ProductCategory, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        # Optional: if you want to store size/color, add those fields to CartItem model
        cart_item.size = size
        cart_item.color = color

        cart_item.save()

        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({'success': True, 'cart_count': cart_count})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)@login_required
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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Order, Cart
from django.conf import settings

@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.items.count() == 0:
        return render(request, 'checkout.html', {'error': 'Cart is empty'})

    total = cart.total_price

    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        payment_method = request.POST['payment_method']

        if payment_method == 'cod':
            total += 200

            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                payment_method='cod',
                total_amount=total,
                paid=False
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    size=item.size,
                    color=item.color
                )

            # ✅ Clear the cart
            cart.items.all().delete()

            send_mail(
                'Order Confirmation',
                f'Thank you {full_name}, your order has been received. Delivery to:\n{address}\nAmount: Ksh.{total}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )

            return redirect('order_list')
        elif payment_method == 'mpesa':
            request.session['checkout_data'] = {
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'address': address,
                'total': str(total)
            }
            return redirect('payment_page')

    return render(request, 'checkout.html', {'total': total})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    latest_status = order.statuses.last().status if order.statuses.exists() else None
    return render(request, 'order_detail.html', {
        'order': order,
        'current_status': latest_status
    })



@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    last_status = order.statuses.last().status if order.statuses.exists() else None
    
    if last_status in [None, 'received']:
        order.delete()  # Or mark as canceled
        messages.success(request, f"Order #{order.id} has been canceled.")
    else:
        messages.error(request, "You can only cancel before delivery starts.")

    return redirect('order_list')


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def toggle_wishlist(request, id):
    product = get_object_or_404(ProductCategory, id=id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
    return redirect('product_detail', id=id)



@login_required
@user_passes_test(lambda u: u.is_superuser)
def analytics_view(request):
    total_users = User.objects.count()
    total_products = ProductCategory.objects.count()
    total_orders = Order.objects.count()
    total_sales = sum(order.total_amount for order in Order.objects.filter(paid=True))
    low_stock_products = ProductCategory.objects.filter(quantity__lt=10)

    return render(request, 'analytics.html', {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'low_stock_products': low_stock_products,
        'products': Product.objects.all(),
        'orders': Order.objects.all(),
    })