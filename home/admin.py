from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, WishList, Order, Review

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'created_at', 'updated_at')
    filter_horizontal = ('images',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'created_at', 'updated_at')
    search_fields = ('alt_text',)
    list_filter = ('created_at', 'updated_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('is_active', 'created_at', 'updated_at')

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'is_notified', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('is_notified', 'created_at', 'updated_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'status', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('status', 'created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('rating', 'created_at', 'updated_at')