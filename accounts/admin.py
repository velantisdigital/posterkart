from django.contrib import admin
from .models import UserProfile, Address


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'state', 'pin_code', 'phone_number', 'is_default')
    list_filter = ('is_default', 'state', 'city')
    search_fields = ('full_name', 'phone_number', 'city', 'pin_code', 'user__username')
