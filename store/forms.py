from django import forms
from django import forms
from .models import Product
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field



class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10, initial=1)

class CheckoutForm(forms.Form):
    card_number = forms.CharField(label="Card Number", required=True)
    card_expiry = forms.CharField(label="Expiry Date (MM/YYYY)", required=True)
    card_type = forms.CharField(label="Card Type", required=True)
    payer_name = forms.CharField(label="Name on Card", required=True)
    street_address = forms.CharField(label="Street Address", required=True)
    city = forms.CharField(label="City", required=True)
    state = forms.CharField(label="State", required=True)
    zip_code = forms.CharField(label="Zip Code", required=True)
    email = forms.CharField(label="Email", required=True)
    phone = forms.CharField(label="Phone", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Define layout with rows and columns for better alignment
        self.helper.layout = Layout(
            Row(
                Column('payer_name', css_class='form-group col-md-4 mb-0 form-control-sm'),
                Column('email', css_class='form-group col-md-4 mb-0 form-control-sm'),
                Column('phone', css_class='form-group col-md-4 mb-0 form-control-sm'),
            ),
            Row(
                Column('card_number', css_class='form-group col-md-6 mb-0 form-control-sm'),
                Column('card_expiry', css_class='form-group col-md-3 mb-0 form-control-sm'),
                Column('card_type', css_class='form-group col-md-3 mb-0 form-control-sm'),
            ),
            Row(
                Column('street_address', css_class='form-group col-md-6 mb-0 form-control-sm'),
                Column('city', css_class='form-group col-md-3 mb-0 form-control-sm'),
                Column('state', css_class='form-group col-md-1 mb-0 form-control-sm'),
                Column('zip_code', css_class='form-group col-md-2 mb-0 form-control-sm'),
            ),
            
        )

class OrderStatusForm(forms.Form):
    order_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control me-2', 'placeholder': "Enter your order number here...", 'type':'search'}),

    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "sku",
            "category",
            "price",
            "quantity",
            "manufacturer",
            "condition",
            "description",
            "image",
        ]
        widgets = {
            "sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter SKU"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Enter price"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter quantity"}),
            "manufacturer": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter manufacturer"}),
            "condition": forms.Select(attrs={"class": "form-select"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Description"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "sku": "SKU",
            "category": "Category",
            "price": "Price",
            "quantity": "Quantity",
            "manufacturer": "Manufacturer",
            "condition": "Condition",
            "description": "Description",
            "image": "Product Image",
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity and quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity

