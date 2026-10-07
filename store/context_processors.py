from .models import Category
from django.conf import settings


def categories_processor(request):
    try:
        categories = Category.objects.filter(is_active=True)
    except Exception:
        categories = []
    return {
        'all_categories': categories,
        'FREE_DELIVERY_THRESHOLD': getattr(settings, 'FREE_DELIVERY_THRESHOLD', 499.00),
        'STANDARD_DELIVERY_CHARGE': getattr(settings, 'STANDARD_DELIVERY_CHARGE', 50.00),
    }
