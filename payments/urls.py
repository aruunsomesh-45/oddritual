from django.urls import path
from .views import create_orders,verify_payments
urlpatterns=[
    path('create-order/',create_orders,name='create_orders'),
    path('verify-payment/',verify_payments,name='verify_payments'),
    
]