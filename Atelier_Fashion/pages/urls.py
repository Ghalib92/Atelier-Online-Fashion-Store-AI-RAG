from django.urls import path, include
from. import views

urlpatterns = [


path('', views.home, name = 'home' ),
path('products/<str:category_name>/', views.category_view, name='category_view'),
path('product/<int:id>/', views.product_detail, name='product_detail'),
path('wishlist/', views.wishlist_view, name='wishlist'),
path('wishlist/<int:id>/', views.toggle_wishlist, name='toggle_wishlist'),
path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/', views.view_cart, name='view_cart'),
path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
path('cart/remove/', views.remove_cart_item, name='remove_cart_item'),
path('search/', views.product_search, name='product_search'),
path('checkout/', views.checkout_view, name='checkout'),
path('orders/', views.my_orders, name='order_list'),
path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
path('analytics/', views.analytics_view, name='analytics'),


]