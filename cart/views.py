from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from decimal import Decimal

from .models import Cart, CartItem, Coupon, Wishlist
from .utils import get_or_create_cart
from store.models import Poster, PosterSize, FrameOption
from customposters.models import CustomPoster


def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('poster', 'custom_poster', 'size', 'frame').all()
    subtotal = cart.get_subtotal()
    delivery_charge = cart.get_delivery_charge()
    discount_amount = cart.get_discount_amount()
    total_amount = cart.get_total()

    # Free delivery calculation
    free_delivery_threshold = Decimal('499.00')
    amount_needed_for_free_delivery = max(Decimal('0.00'), free_delivery_threshold - subtotal)
    delivery_progress_percent = min(100, int((subtotal / free_delivery_threshold) * 100)) if free_delivery_threshold > 0 else 100

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
        'amount_needed_for_free_delivery': amount_needed_for_free_delivery,
        'delivery_progress_percent': delivery_progress_percent,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart_view(request):
    cart = get_or_create_cart(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('ajax') == '1'

    poster_id = request.POST.get('poster_id')
    custom_poster_id = request.POST.get('custom_poster_id')
    size_id = request.POST.get('size_id')
    frame_id = request.POST.get('frame_id')
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    poster = None
    custom_poster = None

    if poster_id:
        poster = get_object_or_404(Poster, pk=poster_id)
    elif custom_poster_id:
        custom_poster = get_object_or_404(CustomPoster, pk=custom_poster_id)
    else:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'No poster specified.'}, status=400)
        messages.error(request, "No poster specified.")
        return redirect('store:shop')

    # Get Size
    if size_id:
        size = get_object_or_404(PosterSize, pk=size_id)
    else:
        size = PosterSize.objects.filter(is_default=True).first() or PosterSize.objects.first()

    # Get Frame
    if frame_id:
        frame = get_object_or_404(FrameOption, pk=frame_id)
    else:
        frame = FrameOption.objects.filter(is_default=True).first() or FrameOption.objects.first()

    # Find existing item or create
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        poster=poster,
        custom_poster=custom_poster,
        size=size,
        frame=frame,
        defaults={'quantity': quantity}
    )

    if not created:
        item.quantity += quantity
        item.save()

    cart.updated_at = cart.updated_at
    cart.save()

    item_title = item.title

    action = request.POST.get('action', 'add')
    if action == 'buy_now':
        return redirect('orders:checkout')

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'message': f'"{item_title}" added to your cart!',
            'cart_count': cart.total_items(),
            'cart_subtotal': float(cart.get_subtotal()),
            'cart_total': float(cart.get_total()),
            'item': {
                'id': item.id,
                'title': item.title,
                'image_url': item.image_url,
                'size': item.size.name if item.size else '',
                'frame': item.frame.name if item.frame else '',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
            }
        })

    messages.success(request, f'"{item_title}" has been added to your cart.')
    return redirect('cart:cart')


@require_POST
def update_cart_item_quantity_view(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('ajax') == '1'

    action = request.POST.get('action')
    quantity = request.POST.get('quantity')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
            item = None
    elif quantity is not None:
        try:
            qty = int(quantity)
            if qty > 0:
                item.quantity = qty
                item.save()
            else:
                item.delete()
                item = None
        except ValueError:
            pass

    cart.refresh_from_db()
    subtotal = cart.get_subtotal()
    delivery = cart.get_delivery_charge()
    discount = cart.get_discount_amount()
    total = cart.get_total()
    cart_count = cart.total_items()

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'item_removed': item is None,
            'item_quantity': item.quantity if item else 0,
            'item_total_price': float(item.total_price) if item else 0.0,
            'cart_count': cart_count,
            'subtotal': float(subtotal),
            'delivery_charge': float(delivery),
            'discount_amount': float(discount),
            'total_amount': float(total),
        })

    return redirect('cart:cart')


@require_POST
def remove_from_cart_view(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item_title = item.title
    item.delete()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'message': f'"{item_title}" removed from cart.',
            'cart_count': cart.total_items(),
            'subtotal': float(cart.get_subtotal()),
            'delivery_charge': float(cart.get_delivery_charge()),
            'discount_amount': float(cart.get_discount_amount()),
            'total_amount': float(cart.get_total()),
        })

    messages.info(request, f'"{item_title}" has been removed from your cart.')
    return redirect('cart:cart')


@require_POST
def apply_coupon_view(request):
    cart = get_or_create_cart(request)
    code = request.POST.get('coupon_code', '').strip().upper()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not code:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Please enter a coupon code.'}, status=400)
        messages.error(request, 'Please enter a coupon code.')
        return redirect('cart:cart')

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': f'Coupon "{code}" is invalid or does not exist.'}, status=400)
        messages.error(request, f'Coupon "{code}" is invalid.')
        return redirect('cart:cart')

    subtotal = cart.get_subtotal()
    is_valid, msg = coupon.is_valid(subtotal)
    if not is_valid:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect('cart:cart')

    cart.coupon = coupon
    cart.save()

    discount = coupon.calculate_discount(subtotal)

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'message': f'Coupon "{coupon.code}" applied! You saved ₹{discount:.2f}',
            'coupon_code': coupon.code,
            'discount_amount': float(discount),
            'subtotal': float(subtotal),
            'delivery_charge': float(cart.get_delivery_charge()),
            'total_amount': float(cart.get_total()),
        })

    messages.success(request, f'Coupon "{coupon.code}" applied! You saved ₹{discount:.2f}')
    return redirect('cart:cart')


@require_POST
def remove_coupon_view(request):
    cart = get_or_create_cart(request)
    cart.coupon = None
    cart.save()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'message': 'Coupon removed.',
            'subtotal': float(cart.get_subtotal()),
            'delivery_charge': float(cart.get_delivery_charge()),
            'discount_amount': 0.0,
            'total_amount': float(cart.get_total()),
        })

    messages.info(request, "Coupon removed.")
    return redirect('cart:cart')


@require_GET
def get_cart_drawer_json_view(request):
    cart = get_or_create_cart(request)
    items = []
    for item in cart.items.select_related('poster', 'custom_poster', 'size', 'frame').all():
        items.append({
            'id': item.id,
            'title': item.title,
            'image_url': item.image_url,
            'size': item.size.name if item.size else '',
            'frame': item.frame.name if item.frame else '',
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'total_price': float(item.total_price),
        })

    return JsonResponse({
        'status': 'success',
        'items': items,
        'cart_count': cart.total_items(),
        'subtotal': float(cart.get_subtotal()),
        'delivery_charge': float(cart.get_delivery_charge()),
        'discount_amount': float(cart.get_discount_amount()),
        'total_amount': float(cart.get_total()),
    })


# Wishlist Views
@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('poster__category')
    return render(request, 'cart/wishlist.html', {'wishlist_items': wishlist_items})


@require_POST
def toggle_wishlist_api(request, poster_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'unauthenticated',
            'message': 'Please login to add posters to your wishlist.',
            'login_url': '/accounts/login/?next=' + request.META.get('HTTP_REFERER', '/')
        }, status=401)

    poster = get_object_or_404(Poster, pk=poster_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, poster=poster).first()

    if wishlist_item:
        wishlist_item.delete()
        action = 'removed'
        msg = f'"{poster.title}" removed from wishlist.'
    else:
        Wishlist.objects.create(user=request.user, poster=poster)
        action = 'added'
        msg = f'"{poster.title}" added to your wishlist ♥'

    count = Wishlist.objects.filter(user=request.user).count()

    return JsonResponse({
        'status': 'success',
        'action': action,
        'message': msg,
        'wishlist_count': count,
    })


@login_required
@require_POST
def move_wishlist_to_cart_view(request, poster_id):
    poster = get_object_or_404(Poster, pk=poster_id)
    Wishlist.objects.filter(user=request.user, poster=poster).delete()

    default_size = PosterSize.objects.filter(is_default=True).first() or PosterSize.objects.first()
    default_frame = FrameOption.objects.filter(is_default=True).first() or FrameOption.objects.first()

    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        poster=poster,
        size=default_size,
        frame=default_frame,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, f'"{poster.title}" moved from wishlist to your cart!')
    return redirect('cart:wishlist')
