

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.db import models
from .models import Product, Cart, CartItem, Category, PaymentDetails, Order, OrderItem
from django.http import HttpResponse, JsonResponse
from cryptography.fernet import Fernet
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from django.contrib import messages
from .forms import CheckoutForm, OrderStatusForm
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Count, Case, When, IntegerField, Sum
import csv
from decimal import Decimal



def about(request):
    categories = Category.objects.all()
    session_id = request.session.get('cart_id') # Retrieve session_id from the user's session
    if not session_id:
        request.session.create()  # Create a session if it doesn't exist
        session_id = request.session.session_key

    # Get the count of CartItems for this session
    cart_items = CartItem.objects.filter(cart__session_id=session_id)
    cart_count = 0
    for item in cart_items:
        cart_count = cart_count + item.quantity
        print(cart_count)
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

    form = OrderStatusForm()
    return render(request, 'store/about.html', 
        {'form': form, 'status': status, 'categories': categories, 'cart_count': cart_count}
    )
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
    categories = Category.objects.all()
    session_id = request.session.get('cart_id') # Retrieve session_id from the user's sessioncity
    product = get_object_or_404(Product, slug=slug)
    cart_items = CartItem.objects.filter(cart__session_id=session_id)
    cart_count = 0
    for item in cart_items:
        cart_count = cart_count + item.quantity
        print(cart_count)

    return render(request, 'store/product_detail.html', {'product': product,
                                                         'cart_count':cart_count,
                                                         'categories': categories})

@login_required
def manage_inventory(request):
    category_filter = request.GET.get('category', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    sku_filter = request.GET.get('sku', '')

    # Base query
    products = Product.objects.all()

    # Apply filters
    if category_filter:
        products = products.filter(category_id=category_filter)
    if manufacturer_filter:
        products = products.filter(manufacturer__icontains=manufacturer_filter)
    if sku_filter:
        products = products.filter(sku__icontains=sku_filter)

    # Check if request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_data = [
            {
                'image': product.image.url if product.image else None,
                'category': product.category.name if product.category else '',
                'manufacturer': product.manufacturer,
                'sku': product.sku,
                'price': str(product.price),
                'quantity': product.quantity,
            }
            for product in products
        ]
        return JsonResponse({'products': products_data})

    # Context for template
    categories = Category.objects.all()
    manufacturers = Product.objects.values_list('manufacturer', flat=True).distinct()

    return render(request, 'store/manage_inventory.html', {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'category_filter': category_filter,
        'manufacturer_filter': manufacturer_filter,
        'sku_filter': sku_filter,
    })



from django.db.models import Q, Count
from django.shortcuts import render
from django.http import HttpResponse

def search_products(request):
    query = request.GET.get('q', '')
    if query:
    # Split the query into individual terms
        query_terms = query.split()

        # Create a base filter for all terms
        query_filter = Q()
        for term in query_terms:
            query_filter |= Q(category__name__icontains=term) | \
                            Q(sku__icontains=term) | \
                            Q(manufacturer__icontains=term) | \
                            Q(description__icontains=term)
            print(query_filter)

        # Annotate each product with a match count
            products = Product.objects.annotate(
                match_count=Sum(
                    Case(
                        When(category__name__icontains=query, then=1),
                        When(sku__icontains=query, then=1),
                        When(manufacturer__icontains=query, then=2),
                        When(description__icontains=query, then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                )
            ).filter(query_filter)
            
            
        

        # Sort by match_count (descending) and limit results
        products = products.order_by('-match_count')[:10]

    else:
        products = Product.objects.none()

    # Render the search results
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
    cart_items = CartItem.objects.filter(cart__session_id=session_id)
    cart_count = 0
    for item in cart_items:
        cart_count = cart_count + item.quantity
        print(cart_count)
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
        'categories': categories,
        'cart_count':cart_count
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
    ca_tax = Decimal("1.0725")
    total_price_with_tax = total_price * ca_tax
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
    state_data = form.cleaned_data.get('state', '') if form.is_valid() else ''
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'form': form,
        'total_price': total_price,
        'total_price_with_tax': total_price_with_tax,
        'state_data': state_data,
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
        order_number = request.POST.get('order_number')  
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
                status = order.status  
            except:
                messages.error(request, "Order not found. Please check the order number and try again.")
        else:
            messages.error(request, "Please enter an order number.")

    return render(request, 'store/about.html', {'status': status, 'categories': categories, 'order_number': order_number})

def show_receipt(request, order_number):
    # Retrieve the main order and related payment details
    categories = Category.objects.all()
    order = get_object_or_404(Order, order_number=order_number)
    payment_details = order.paymentdetails  # Assuming there's a related PaymentDetails instance
    order_items = OrderItem.objects.filter(order=order)  # Retrieve all items associated with this order
    total_price = sum(item.price * item.quantity for item in order_items)
    ca_tax = Decimal("1.0725")
    total_price_with_tax = total_price * ca_tax
    # Decrypt the card number if payment details are available
    decrypted_card_number = payment_details.get_card_number() if payment_details else None

    context = {
        'order': order,
        'order_items': order_items,  # Pass order items to the template
        'payment_details': payment_details,
        'decrypted_card_number': decrypted_card_number,
        'total_price': total_price,
        'categories': categories,
        'total_price_with_tax': total_price_with_tax
    }
    return render(request, 'store/receipt.html', context)

def export_inventory(request):
    # Export products to CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'

    writer = csv.writer(response)
    # Write header row
    writer.writerow(['SKU', 'Category', 'Manufacturer', 'Description', 'Price', 'Quantity', 'Condition'])

    # Write product data
    for product in Product.objects.all():
        writer.writerow([
            product.sku,
            product.category.name if product.category else '',
            product.manufacturer,
            product.description,
            product.price,
            product.quantity,
            product.condition,
        ])

    return response


import csv
import os
import zipfile
from io import TextIOWrapper
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.core.files.storage import default_storage
from .models import Category, Product
from django.utils.text import slugify
import shutil
import pandas as pd

def import_inventory(request):
    if request.method == 'POST' and request.FILES.get('csv_file') and request.FILES.get('zip_file'):
        csv_file = request.FILES['csv_file']
        zip_file = request.FILES['zip_file']
        
        # Extract images from the zip file
        image_dir = 'temp_images/'  # Temporary directory to store extracted images
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(image_dir)
        
        # Read CSV file
        decoded_file = TextIOWrapper(csv_file, encoding='utf-8-sig')  # Use utf-8-sig to handle BOM
        reader = csv.DictReader(decoded_file)

        for row in reader:
            
            category, _ = Category.objects.get_or_create(name=row['category'])
            image_filename = row['image']  # Assuming CSV has an 'ImageFilename' column
            image_path = os.path.join(image_dir, image_filename)

            # Check if the image exists in the extracted folder
            image_file = None
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img:
                    image_file = ContentFile(img.read(), name=image_filename)
            sku = row.get('sku')
            slug = slugify(sku)
            # Create or update product
            Product.objects.update_or_create(
                sku=sku,
                defaults={
                    #'name': row['Name'],
                    'category': category,
                    'manufacturer': row['manufacturer'],
                    'description': row['description'],
                    'price': row['price'],
                    'quantity': row['quantity'],
                    'condition': row.get('condition', ''),
                    'image': image_file if image_file else None,
                    'slug': slug,
                },
            )

        # Cleanup extracted images
        for file in os.listdir(image_dir):
            file_path = os.path.join(image_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        shutil.rmtree(image_dir)
        messages.success(request, "Inventory updated successfully!")

    return redirect('manage_inventory')

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product
from .forms import ProductForm
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import json

@login_required
def update_product(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        # Populate the form with the POST data
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Product updated successfully!"})
            return redirect("manage_inventory")  # Redirect back to inventory management page
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})
            return redirect("manage_inventory")  # Optionally handle errors differently for non-AJAX requests

    # Fallback for non-POST requests
    return redirect("manage_inventory")

@login_required
@csrf_protect  # Since we're using AJAX, this helps with CSRF protection (already included in JS)
def mass_update_inventory(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            for product_id, updates in data.items():
                product = Product.objects.get(id=product_id)
                if "price" in updates:
                    product.price = float(updates["price"])
                if "quantity" in updates:
                    product.quantity = int(updates["quantity"])
                product.save()

            return JsonResponse({"message": "Inventory updated successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.shortcuts import HttpResponse
from django.utils.feedgenerator import rfc2822_date
from xml.etree.ElementTree import Element, SubElement, tostring
from .models import Product  # Update this with your actual product model

def google_merchant_feed(request):
    # Create the XML structure
    rss = Element("rss", {"xmlns:g": "http://base.google.com/ns/1.0", "version": "2.0"})
    channel = SubElement(rss, "channel")

    # Add feed metadata
    SubElement(channel, "title").text = "Your Store Name"
    SubElement(channel, "link").text = "https://yourstore.com"
    SubElement(channel, "description").text = "Your store's product feed for Google Merchant Center"

    # Fetch all products from the database
    products = Product.objects.all() # Adjust query as needed

    for product in products:
        item = SubElement(channel, "item")
        SubElement(item, "g:id").text = "N/A"
        SubElement(item, "title").text = product.sku
        SubElement(item, "description").text = product.description[:4999]  # Limit to Google's max length
        SubElement(item, "link").text = f"https://yourstore.com/products/{product.slug}"
        image_url = product.image.url if product.image else "N/A"
        SubElement(item, "g:image_link").text = image_url
        SubElement(item, "g:price").text = f"{product.price} USD"  # Adjust currency if needed
        SubElement(item, "g:availability").text = "in_stock" if product.quantity != None and product.quantity > 0 else "out_of_stock"
        SubElement(item, "g:brand").text = product.manufacturer if product.manufacturer else "Unknown"
        SubElement(item, "g:condition").text = "new"  # Assuming new products
        #SubElement(item, "g:gtin").text = product.gtin if product.gtin else "N/A"
        #SubElement(item, "g:mpn").text = product.mpn if product.mpn else "N/A"
        #SubElement(item, "g:shipping").text = "5.00 USD"  # Adjust shipping cost
        SubElement(item, "g:category").text = product.category.google_category if product.category else "N/A"
    # Convert XML to string
    xml_string = tostring(rss, encoding="utf-8")

    # Return XML response
    response = HttpResponse(xml_string, content_type="application/xml")
    response['Content-Disposition'] = 'attachment; filename="google_merchant_feed.xml"'
    return response
