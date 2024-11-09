
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from store.models import Order, OrderItem, Category
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

@login_required
def unprocessed_orders(request):
    categories = Category.objects.all()
    unprocessed_orders = Order.objects.filter(is_processed=False)
    return render(request, 'order_processing/unprocessed_orders.html', {
        'orders': unprocessed_orders,
        'categories': categories
    })


@login_required
def processed_orders(request):
    orders = Order.objects.all().filter(is_processed=True)
    categories = Category.objects.all()

    # Get search parameters
    order_number = request.GET.get('order_number', '')
    payer_name = request.GET.get('payer_name', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter by order number or payer name
    if order_number:
        orders = orders.filter(order_number__icontains=order_number)
    if payer_name:
        orders = orders.filter(payer_name__icontains=payer_name)

    # Filter by date
    if start_date:
        orders = orders.filter(created_at__gte=timezone.datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        orders = orders.filter(created_at__lte=timezone.datetime.strptime(end_date, '%Y-%m-%d'))

    context = {
        'orders': orders,
        'categories': categories
    }
    return render(request, 'order_processing/processed_orders.html', context)


@login_required
def process_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_processed = True
    order.save()
    return redirect('order_processing:unprocessed_orders')

@login_required
def order_detail(request, order_number):
    # Retrieve the main order and related payment details
    categories = Category.objects.all()
    order = get_object_or_404(Order, order_number=order_number)
    payment_details = order.paymentdetails  # Assuming there's a related PaymentDetails instance
    order_items = OrderItem.objects.filter(order=order)  # Retrieve all items associated with this order
    total_price = sum(item.price * item.quantity for item in order_items)
    # Decrypt the card number if payment details are available
    decrypted_card_number = payment_details.get_card_number() if payment_details else None

    if request.method == 'POST':
        # Toggle order processed status
        if 'toggle_processed' in request.POST:
            order.is_processed = not order.is_processed
            order.save()
            messages.success(request, f'Order processed status updated to {order.is_processed}.')
            return redirect('order_processing:order_detail', order_number=order_number)

        # Update order status if provided
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, 'Order status updated successfully.')
            return redirect('order_processing:order_detail', order_number=order_number)

    context = {
        'order': order,
        'order_items': order_items,  # Pass order items to the template
        'payment_details': payment_details,
        'decrypted_card_number': decrypted_card_number,
        'total_price': total_price,
        'categories': categories
    }
    return render(request, 'order_processing/order_detail.html', context)