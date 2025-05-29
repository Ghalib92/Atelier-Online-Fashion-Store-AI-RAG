import json
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from pages.models import Cart  # adjust based on your actual cart model
from .models import PaymentTransaction
from django.contrib.auth.decorators import login_required
from .mpesa import lipa_na_mpesa

@login_required
def payment_page(request):
    cart = Cart.objects.filter(user=request.user).first()
    total = cart.total_price if cart else 0
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if total > 0:
            response = initiate_payment(phone, total, request.user)
            return render(request, 'pay.html', {'total': total, 'message': response})
    return render(request, 'pay.html', {'total': total})
def initiate_payment(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        cart = Cart.objects.get(user=request.user)
        amount = cart.total_price if cart else 0
        response = lipa_na_mpesa(phone, amount, request.user.username)
        
        # Save transaction
        PaymentTransaction.objects.create(
            user=request.user,
            phone=phone,
            amount=amount,
            checkout_request_id=response.get('CheckoutRequestID'),
            status="Pending"
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    body = data.get('Body', {})
    stk_callback = body.get('stkCallback', {})
    
    checkout_id = stk_callback.get('CheckoutRequestID')
    result_code = stk_callback.get('ResultCode')
    metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

    amount_paid = 0
    phone = ''
    for item in metadata:
        if item['Name'] == 'Amount':
            amount_paid = item['Value']
        if item['Name'] == 'PhoneNumber':
            phone = str(item['Value'])

    try:
        txn = PaymentTransaction.objects.get(checkout_request_id=checkout_id)
        cart = Cart.objects.get(user=txn.user)
        cart_total = cart.get_total()

        if result_code == 0 and int(amount_paid) == int(cart_total):
            txn.status = 'Success'
            txn.paid_at = timezone.now()
            txn.save()

            # Clear cart
            cart.items.all().delete()
            return redirect('payment_success')

        txn.status = 'Failed'
        txn.save()

    except PaymentTransaction.DoesNotExist:
        pass

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

def payment_success(request):
    return render(request, 'success.html')
