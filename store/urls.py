from django.urls import path
from . import views


urlpatterns = [
    path('', views.about, name='about'),
    path('about', views.about, name='about'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search_products, name='search_products'),
    path('product/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_summary, name='cart_summary'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'), 
    path('order-success/<uuid:order_number>/', views.order_success, name='order_success'),
    path('check-order-status/', views.check_order_status, name='check_order_status'),
    
]
