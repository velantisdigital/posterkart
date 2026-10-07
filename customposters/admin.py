from django.contrib import admin
from .models import CustomPoster


@admin.register(CustomPoster)
class CustomPosterAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'size', 'frame', 'quantity', 'total_price', 'created_at')
    list_filter = ('size', 'frame', 'created_at')
    search_fields = ('user__username', 'custom_text', 'special_instructions')
    readonly_fields = ('created_at',)
