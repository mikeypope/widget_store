

# Create your models here.
from django.db import models
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    google_category = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=200, blank=True)  
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    description = models.TextField(blank=True)  
    image = models.ImageField(upload_to='products/', blank=True, null=True)  
    slug = models.SlugField(unique=True, blank=True)  
    quantity = models.IntegerField(null=True, blank=True)  
    manufacturer = models.CharField(max_length=100, blank=True)  
    condition = models.CharField(max_length=50, blank=True, null=True)  

    def __str__(self):
        return self.slug if self.slug else f"Product {self.id}"

class Cart(models.Model):
    session_id = models.CharField(max_length=200, unique=True)  # Ensure session_id is unique
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

# Encryption Helper
def encrypt_data(data):
    cipher_suite = Fernet(settings.ENCRYPTION_KEY)  # Load this key from your settings securely
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    cipher_suite = Fernet(settings.ENCRYPTION_KEY)
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

class PaymentDetails(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    
    # Store the encrypted card number
    card_number_encrypted = models.TextField()
    
    # Masked card number for display purposes
    masked_card_number = models.CharField(max_length=19, blank=True, null=True)
    
    card_expiry = models.CharField(max_length=7)  # MM/YYYY format
    card_type = models.CharField(max_length=20, blank=True, null=True)
    payer_name = models.CharField(max_length=100)
    
    # Discrete address fields
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)

    # Contact info
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

    def set_card_number(self, card_number):
        """Encrypt and set the card number, also generate the masked version."""
        self.card_number_encrypted = encrypt_data(card_number)
        self.masked_card_number = f"**** **** **** {card_number[-4:]}"  # Masking the card number

    def get_card_number(self):
    # Ensure card_number_encrypted is not None before attempting decryption
        if self.card_number_encrypted:
            try:
                return decrypt_data(self.card_number_encrypted)
            except InvalidToken:
                return None  # Handle invalid tokens gracefully
        return None

    def save(self, *args, **kwargs):
        """Override save method to ensure masked card number is set."""
        if not self.masked_card_number:
            # Generate the masked card number if not set
            decrypted_card_number = self.get_card_number()
            self.masked_card_number = f"**** **** **** {decrypted_card_number[-4:]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PaymentDetails for Order {self.order.order_number}"

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(default='Pending', max_length=100)
    payer_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Order {self.order_number}"

# OrderItem model for tracking individual items in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.sku} (x{self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.price