from django.urls import path
from . import views

urlpatterns = [
    path("chatbot-page/", views.chatbot_page, name="chatbot-page"),
    path('get/',views.get_response, name='get_response'),
   
     
     
     ]
