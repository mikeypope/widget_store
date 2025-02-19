from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.about, name='about'),
    path('about', views.about, name='about'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search_products, name='search_products'),
    path('manage-inventory/', views.manage_inventory, name='manage_inventory'),
    path('export-inventory/', views.export_inventory, name='export_inventory'),
    path('import-inventory/', views.import_inventory, name='import_inventory'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('mass-update-inventory/', views.mass_update_inventory, name="mass_update_inventory"),
    path('product/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_summary, name='cart_summary'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'), 
    path('order-success/<uuid:order_number>/', views.order_success, name='order_success'),
    path('check-order-status/', views.check_order_status, name='check_order_status'),
    path('show-receipt/<str:order_number>/', views.show_receipt, name='show_receipt'),
    path("google-merchant-feed.xml", views.google_merchant_feed, name="google_merchant_feed"),
    
] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
