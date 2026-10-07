from django.contrib import admin
from .models import Coupon, Cart, CartItem, Wishlist


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'active', 'used_count', 'usage_limit', 'expiry_date')
    list_filter = ('active', 'discount_type')
    search_fields = ('code',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'coupon', 'created_at', 'updated_at')
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'poster', 'created_at')
    search_fields = ('user__username', 'poster__title')
