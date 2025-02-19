from django.urls import path
from . import views

app_name = 'order_processing'

urlpatterns = [
    path('unprocessed-orders/', views.unprocessed_orders, name='unprocessed_orders'),
    path('process-order/<int:order_id>/', views.process_order, name='process_order'),
    path('complete-order/<int:order_id>/', views.complete_order, name='complete_order'),
     path('order/<uuid:order_number>/', views.order_detail, name='order_detail'),
     path('processed-orders/', views.processed_orders, name='processed_orders'),
     path('completed-orders/', views.completed_orders, name='completed_orders'),
     path('decrypted-card-number/<uuid:order_number>/', views.decrypted_card_number, name='decrypted_card_number'),
]
