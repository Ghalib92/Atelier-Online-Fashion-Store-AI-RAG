from django.urls import path
from . import views

urlpatterns = [
    path('pay/', views.payment_page, name='payment_page'),
     
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('orders/', views.my_orders, name='order_list'),
]
