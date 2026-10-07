from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal

from .models import CustomPoster
from .forms import CustomPosterForm
from store.models import PosterSize, FrameOption
from cart.utils import get_or_create_cart
from cart.models import CartItem


def create_custom_poster_view(request):
    sizes = PosterSize.objects.filter(is_active=True).order_by('sort_order', 'extra_price')
    frames = FrameOption.objects.filter(is_active=True).order_by('sort_order', 'extra_price')
    base_custom_price = Decimal('349.00')

    if request.method == 'POST':
        form = CustomPosterForm(request.POST, request.FILES)
        if form.is_valid():
            custom_poster = form.save(commit=False)
            if request.user.is_authenticated:
                custom_poster.user = request.user
            else:
                if not request.session.session_key:
                    request.session.save()
                custom_poster.session_key = request.session.session_key
            custom_poster.base_price = base_custom_price
            custom_poster.save()

            # Add to cart
            cart = get_or_create_cart(request)
            CartItem.objects.create(
                cart=cart,
                custom_poster=custom_poster,
                size=custom_poster.size,
                frame=custom_poster.frame,
                quantity=custom_poster.quantity
            )

            action = request.POST.get('action', 'add_to_cart')
            messages.success(request, "Your custom poster has been created and added to your cart!")

            if action == 'buy_now':
                return redirect('orders:checkout')
            return redirect('cart:cart')
        else:
            messages.error(request, "Please check the form inputs and ensure an image is uploaded.")
    else:
        default_size = sizes.filter(is_default=True).first() or sizes.first()
        default_frame = frames.filter(is_default=True).first() or frames.first()
        form = CustomPosterForm(initial={'size': default_size, 'frame': default_frame, 'quantity': 1})

    context = {
        'form': form,
        'sizes': sizes,
        'frames': frames,
        'base_custom_price': base_custom_price,
    }
    return render(request, 'customposters/create_custom_poster.html', context)
