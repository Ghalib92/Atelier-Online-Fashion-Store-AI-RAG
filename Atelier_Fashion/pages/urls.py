from django.urls import path, include
from. import views

urlpatterns = [


path('', views.home, name = 'home' ),
path('products/<str:category_name>/', views.category_view, name='category_view'),
path('product/<int:id>/', views.product_detail, name='product_detail'),
path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/', views.view_cart, name='view_cart'),
path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
path('cart/remove/', views.remove_cart_item, name='remove_cart_item'),
path('search/', views.product_search, name='product_search'),
path('checkout/', views.checkout_view, name='checkout'),


]