from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
import uuid

from .models import Order, OrderItem
from cart.utils import get_or_create_cart
from accounts.models import Address
from accounts.forms import AddressForm


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('poster', 'custom_poster', 'size', 'frame').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Please add some posters before checking out.")
        return redirect('store:shop')

    addresses = Address.objects.filter(user=request.user)
    subtotal = cart.get_subtotal()
    delivery_charge = cart.get_delivery_charge()
    discount_amount = cart.get_discount_amount()
    total_amount = cart.get_total()

    address_form = AddressForm()

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', 'DEMO_ONLINE')

        # Handle creating new address directly from checkout if chosen
        if address_id == 'new':
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                selected_address = address_form.save(commit=False)
                selected_address.user = request.user
                selected_address.save()
            else:
                messages.error(request, "Please check the delivery address details.")
                return render(request, 'orders/checkout.html', {
                    'cart': cart,
                    'cart_items': cart_items,
                    'addresses': addresses,
                    'address_form': address_form,
                    'subtotal': subtotal,
                    'delivery_charge': delivery_charge,
                    'discount_amount': discount_amount,
                    'total_amount': total_amount,
                })
        else:
            selected_address = get_object_or_404(Address, id=address_id, user=request.user)

        # Create Order securely on backend
        order = Order.objects.create(
            user=request.user,
            delivery_address=selected_address,
            shipping_full_name=selected_address.full_name,
            shipping_phone=selected_address.phone_number,
            shipping_address_line1=selected_address.address_line_1,
            shipping_address_line2=selected_address.address_line_2,
            shipping_city=selected_address.city,
            shipping_state=selected_address.state,
            shipping_pin_code=selected_address.pin_code,
            shipping_landmark=selected_address.landmark,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            discount_amount=discount_amount,
            total_amount=total_amount,
            coupon_code=cart.coupon.code if cart.coupon else '',
            payment_method=payment_method,
            payment_status='PENDING',
            order_status='PLACED'
        )

        # Create OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                poster=item.poster,
                custom_poster=item.custom_poster,
                title=item.title,
                image_url=item.image_url,
                size_name=item.size.name if item.size else 'Standard',
                frame_name=item.frame.name if item.frame else 'No Frame',
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )

        if payment_method == 'COD':
            # Clear cart
            cart.items.all().delete()
            cart.coupon = None
            cart.save()
            messages.success(request, f"Order #{order.order_number} has been placed successfully!")
            return redirect('orders:order_success', order_number=order.order_number)
        else:
            # Redirect to demo payment gateway simulator
            return redirect('orders:demo_payment', order_number=order.order_number)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'address_form': address_form,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def demo_payment_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.payment_status == 'PAID':
        return redirect('orders:order_success', order_number=order.order_number)

    if request.method == 'POST':
        action = request.POST.get('action', 'success')
        if action == 'success':
            order.payment_status = 'PAID'
            order.payment_transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            order.order_status = 'CONFIRMED'
            order.save()

            # Clear cart
            cart = get_or_create_cart(request)
            cart.items.all().delete()
            cart.coupon = None
            cart.save()

            messages.success(request, "Payment successful! Your order has been confirmed.")
            return redirect('orders:order_success', order_number=order.order_number)
        else:
            order.payment_status = 'FAILED'
            order.save()
            messages.error(request, "Payment failed or was cancelled. You can retry paying anytime.")
            return redirect('orders:order_detail', order_number=order.order_number)

    context = {
        'order': order,
    }
    return render(request, 'orders/demo_payment.html', context)


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number, user=request.user)
    estimated_delivery = order.created_at + timezone.timedelta(days=4)

    context = {
        'order': order,
        'estimated_delivery': estimated_delivery,
    }
    return render(request, 'orders/order_success.html', context)


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    
    filter_status = request.GET.get('status', 'all')
    if filter_status == 'active':
        orders = orders.filter(order_status__in=['PLACED', 'CONFIRMED', 'PRINTING', 'SHIPPED', 'OUT_FOR_DELIVERY'])
    elif filter_status == 'delivered':
        orders = orders.filter(order_status='DELIVERED')
    elif filter_status == 'cancelled':
        orders = orders.filter(order_status='CANCELLED')

    context = {
        'orders': orders,
        'filter_status': filter_status,
        'total_orders': Order.objects.filter(user=request.user).count(),
    }
    return render(request, 'orders/my_orders.html', context)


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number, user=request.user)
    estimated_delivery = order.created_at + timezone.timedelta(days=4)

    context = {
        'order': order,
        'estimated_delivery': estimated_delivery,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_tracking_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    estimated_delivery = order.created_at + timezone.timedelta(days=4)

    context = {
        'order': order,
        'estimated_delivery': estimated_delivery,
    }
    return render(request, 'orders/order_tracking.html', context)


@login_required
def cancel_order_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if not order.can_cancel:
        messages.error(request, "This order has already been shipped or delivered and cannot be cancelled.")
        return redirect('orders:order_detail', order_number=order.order_number)

    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', '').strip()
        order.order_status = 'CANCELLED'
        order.cancellation_reason = reason or 'Cancelled by customer'
        if order.payment_status == 'PAID':
            order.payment_status = 'REFUNDED'
        order.save()

        messages.info(request, f"Order #{order.order_number} has been cancelled.")
        return redirect('orders:order_detail', order_number=order.order_number)

    return render(request, 'orders/order_cancel_confirm.html', {'order': order})
