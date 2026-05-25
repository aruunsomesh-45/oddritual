from django.urls import path 
from . import views 

urlpatterns = [ 
    path('',views.home, name='home'), 
    path('about/',views.about, name='about'),
    path('p/<str:pid>/',views.product_detail,name='product_detail'),
    path('shop/', views.shop, name='shop'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<str:pid>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
]