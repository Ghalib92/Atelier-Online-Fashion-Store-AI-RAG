from django.urls import path, include
from. import views

urlpatterns = [


path('', views.home, name = 'home' ),
path('graduation/',views.graduation,name = 'graduation'),


]