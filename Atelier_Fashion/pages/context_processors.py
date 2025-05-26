def cart_context(request):
    return {
        'global_cart_count': request.session.get('cart_count', 0),
        'cart_items': request.session.get('cart', {})
    }