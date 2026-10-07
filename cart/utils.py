from .models import Cart, CartItem


def get_or_create_cart(request):
    """
    Get or create a Cart for the current request.
    Handles merging anonymous cart into user cart upon login seamlessly.
    """
    if request.user.is_authenticated:
        # Check if there is a session cart to merge
        session_key = request.session.session_key
        user_cart, _ = Cart.objects.get_or_create(user=request.user)

        if session_key:
            guest_carts = Cart.objects.filter(session_key=session_key, user__isnull=True)
            for guest_cart in guest_carts:
                for item in guest_cart.items.all():
                    # Check if matching item exists in user_cart
                    existing_item = user_cart.items.filter(
                        poster=item.poster,
                        custom_poster=item.custom_poster,
                        size=item.size,
                        frame=item.frame
                    ).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = user_cart
                        item.save()
                guest_cart.delete()

        return user_cart
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart
