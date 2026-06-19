from django.urls import path

from .views import MpesaCallbackView, STKPushView, TransactionListView

urlpatterns = [
    path("stk-push/", STKPushView.as_view(), name="stk_push"),
    path("mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa_callback"),
    path("transactions/", TransactionListView.as_view(), name="transactions"),
]
