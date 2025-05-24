from django.urls import path, include
from. import views

urlpatterns = [


path('', views.home, name = 'home' ),
path('products/<str:category_name>/', views.category_view, name='category_view'),



]