
from django.contrib import admin
from .models import Category, Product, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'google_category']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'slug', 'category', 'price', 'image','description']
    list_filter = ['category', 'sku']
    list_editable = ['price','image','description']
    prepopulated_fields = {'slug': ('slug',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'created_at', 'is_processed', 'is_complete', 'status', 'payer_name']
    list_filter = ['is_processed', 'is_complete', 'status']
    search_fields = ['order_number', 'payer_name']
    actions = ['mark_processed', 'mark_completed']

    def mark_processed(self, request, queryset):
        queryset.update(is_processed=True)
    mark_processed.short_description = "Mark selected orders as processed"

    def mark_completed(self, request, queryset):
        queryset.update(is_complete=True)
    mark_completed.short_description = "Mark selected orders as completed"