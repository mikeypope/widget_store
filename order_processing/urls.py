from django.urls import path
from . import views

app_name = 'order_processing'

urlpatterns = [
    path('unprocessed-orders/', views.unprocessed_orders, name='unprocessed_orders'),
    path('process-order/<int:order_id>/', views.process_order, name='process_order'),
     path('order/<uuid:order_number>/', views.order_detail, name='order_detail'),
     path('processed-orders/', views.processed_orders, name='processed_orders'),
]
