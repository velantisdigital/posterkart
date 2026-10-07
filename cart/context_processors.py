from .utils import get_or_create_cart
from .models import Wishlist


def cart_and_wishlist_processor(request):
    try:
        cart = get_or_create_cart(request)
        cart_items_count = cart.total_items()
        cart_subtotal = cart.get_subtotal()
        cart_items = cart.items.select_related('poster', 'custom_poster', 'size', 'frame').all()
    except Exception:
        cart = None
        cart_items_count = 0
        cart_subtotal = 0
        cart_items = []

    wishlist_count = 0
    wishlist_poster_ids = []
    if request.user.is_authenticated:
        try:
            wishlist_items = Wishlist.objects.filter(user=request.user)
            wishlist_count = wishlist_items.count()
            wishlist_poster_ids = list(wishlist_items.values_list('poster_id', flat=True))
        except Exception:
            wishlist_count = 0
            wishlist_poster_ids = []

    return {
        'cart': cart,
        'cart_items_count': cart_items_count,
        'cart_subtotal': cart_subtotal,
        'drawer_cart_items': cart_items,
        'wishlist_count': wishlist_count,
        'wishlist_poster_ids': wishlist_poster_ids,
    }
