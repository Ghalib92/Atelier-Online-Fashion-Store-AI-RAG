from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = sum(item.quantity for item in cart.items.all()) if cart else 0
    else:
        count = 0
    return {'cart_items_count': count}
