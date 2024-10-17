from django.contrib import admin
from .models import CustomUser, Product, Order, GroupBuy, Review, ProductImage, Category


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('role',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'get_seller', 'created_at')
    list_filter = ('category', 'brand', 'in_stock', 'created_at')
    search_fields = ('name', 'description', 'brand')
    inlines = [ProductImageInline]

    def get_seller(self, obj):
        return obj.seller.username
    get_seller.short_description = 'Seller'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)

@admin.register(GroupBuy)
class GroupBuyAdmin(admin.ModelAdmin):
    list_display = ('product', 'min_participants', 'end_date', 'status')
    list_filter = ('status', 'end_date')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username')
