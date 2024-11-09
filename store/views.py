

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.db import models
from .models import Product, Cart, CartItem, Category, PaymentDetails, Order, OrderItem
from django.http import HttpResponse
from django.db.models import Q  # Import Q for complex queries
from cryptography.fernet import Fernet
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from django.contrib import messages
from .forms import CheckoutForm, OrderStatusForm
from django.db import transaction


def about(request):
    categories = Category.objects.all()
    return render(request, 'store/about.html', {
        'categories': categories
    })
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()  # Fetch categories to pass to the template
    products = Product.objects.all()
    
    # Filter by category if provided
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        manufacturers = products.values_list('manufacturer', flat=True).distinct().order_by('manufacturer')  # Get unique manufacturers

    # Filter by manufacturer if provided in the request
    selected_manufacturer = request.GET.get('manufacturer')
    if selected_manufacturer:
        products = products.filter(manufacturer=selected_manufacturer)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'selected_manufacturer': selected_manufacturer,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    category = None
    categories = Category.objects.all() 
    return render(request, 'store/product_detail.html', {'product': product, 'categories': categories})

def search_products(request):
    query = request.GET.get('q', '')
    if query:
        # Search by name, sku, or description
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(manufacturer__icontains=query) | 
            Q(description__icontains=query)
        )[:10]  # Limit to top 5 results
    else:
        products = Product.objects.none()

    # Render only the search results and return as a response
    html = render(request, 'store/search_results.html', {'products': products}).content.decode('utf-8')
    return HttpResponse(html)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the session has a cart ID; if not, create a new cart
    session_id = request.session.get('cart_id')
    if not session_id:
        session_id = get_random_string(32)
        request.session['cart_id'] = session_id
        cart = Cart.objects.create(session_id=session_id)
        
    else:
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        
        
    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If it already exists, just increase the quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Item added to cart.")
    

    # Redirect back to the product detail page or cart page
    return redirect('cart_summary')

def cart_summary(request):
    categories = None
    categories = Category.objects.all() 
    # Retrieve the cart by session ID
    session_id = request.session.get('cart_id')
    if not session_id:
        # If no cart session, pass an empty cart
        cart_items = []
        total_price = 0
    else:
        # Retrieve the cart and its items
        cart = Cart.objects.filter(session_id=session_id).first()
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'store/cart_summary.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'categories': categories
    })

def remove_from_cart(request, item_id):
    # Retrieve the CartItem by ID and delete it
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    
    # Redirect back to the cart summary page
    return redirect('cart_summary')


def update_cart_item(request, item_id):
    if request.method == 'POST':
        # Retrieve the CartItem and update its quantity
        cart_item = get_object_or_404(CartItem, id=item_id)
        new_quantity = int(request.POST.get('quantity', 1))
        
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Quantity updated to {new_quantity}.")
        else:
            # If quantity is zero or less, remove the item from the cart
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
        
        # Redirect back to the cart summary page
        return redirect('cart_summary')
    
def checkout(request):
    categories = Category.objects.all()
    session_id = request.session.get('cart_id')  # Retrieve the cart ID from session
    if not session_id:
        messages.warning(request, "Your cart is empty. Please add items to your cart before checking out.")
        return redirect('cart_summary')

    cart = Cart.objects.filter(session_id=session_id).first()
    if not cart:
        messages.warning(request, "Your cart is empty. Please add items to your cart before checking out.")
        return redirect('cart_summary')

    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create the main order instance
                order = Order.objects.create(
                    status='Pending',
                    payer_name=form.cleaned_data['payer_name']
                )
                order_number = order.order_number

                # Create an OrderItem for each item in the cart
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                        

                    )

                # Add payment details to the order
                payment = PaymentDetails(
                    order=order,
                    card_expiry=form.cleaned_data['card_expiry'],
                    card_type=form.cleaned_data['card_type'],
                    payer_name=form.cleaned_data['payer_name'],
                    street_address=form.cleaned_data['street_address'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    zip_code=form.cleaned_data['zip_code'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone']
                )
                payment.set_card_number(form.cleaned_data['card_number'])
                payment.save()

                # Clear the cart after placing the order
                cart_items.delete()
                messages.success(request, "Order placed successfully!")
                return redirect('order_success', order_number=order_number)

    else:
        form = CheckoutForm()

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'form': form,
        'total_price': total_price,
        'categories': categories
    })

def order_success(request, order_number):
    categories = Category.objects.all()
    return render(request, 'store/order_success.html', {
        'order_number': order_number,
        'categories': categories
    })

def check_order_status(request):
    categories = Category.objects.all()
    status = None
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            order_number = form.cleaned_data['order_number']
            try:
                order = Order.objects.get(order_number=order_number)
                status = order.status  # Assuming your Order model has a 'status' field
            except Order.DoesNotExist:
                messages.error(request, "Order not found. Please check the order number and try again.")
    else:
        form = OrderStatusForm()

    return render(request, 'store/order_status.html', {'form': form, 'status': status, 'categories': categories})