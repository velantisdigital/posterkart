import uuid
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from accounts.models import Address
from store.models import Poster
from customposters.models import CustomPoster


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('DEMO_ONLINE', 'Demo Online Payment (Cards / UPI / NetBanking)'),
        ('RAZORPAY', 'Razorpay Gateway (Production Ready)'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Payment Successful'),
        ('FAILED', 'Payment Failed'),
        ('REFUNDED', 'Refunded'),
    )

    ORDER_STATUS_CHOICES = (
        ('PLACED', 'Order Placed'),
        ('CONFIRMED', 'Confirmed'),
        ('PRINTING', 'Printing'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    order_number = models.CharField(max_length=60, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    # Address snapshot at time of checkout
    shipping_full_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=20)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pin_code = models.CharField(max_length=10)
    shipping_landmark = models.CharField(max_length=150, blank=True)

    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    coupon_code = models.CharField(max_length=50, blank=True)

    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='DEMO_ONLINE')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_transaction_id = models.CharField(max_length=100, blank=True)

    # Tracking & Status
    order_status = models.CharField(max_length=25, choices=ORDER_STATUS_CHOICES, default='PLACED')
    cancellation_reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} ({self.user.username})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_str = self.created_at.strftime('%Y%m%d') if self.created_at else timezone_date_str()
            random_suffix = uuid.uuid4().hex[:6].upper()
            self.order_number = f"PK-{date_str}-{random_suffix}"
        super().save(*args, **kwargs)

    @property
    def can_cancel(self):
        return self.order_status in ['PLACED', 'CONFIRMED', 'PRINTING']

    @property
    def status_step(self):
        steps = {
            'PLACED': 1,
            'CONFIRMED': 2,
            'PRINTING': 3,
            'SHIPPED': 4,
            'OUT_FOR_DELIVERY': 5,
            'DELIVERED': 6,
            'CANCELLED': 0,
        }
        return steps.get(self.order_status, 1)

    @property
    def formatted_shipping_address(self):
        parts = [self.shipping_address_line1]
        if self.shipping_address_line2:
            parts.append(self.shipping_address_line2)
        if self.shipping_landmark:
            parts.append(f"Near {self.shipping_landmark}")
        parts.append(f"{self.shipping_city}, {self.shipping_state} - {self.shipping_pin_code}")
        return ", ".join(parts)


def timezone_date_str():
    from django.utils import timezone
    return timezone.now().strftime('%Y%m%d')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    poster = models.ForeignKey(Poster, on_delete=models.SET_NULL, null=True, blank=True)
    custom_poster = models.ForeignKey(CustomPoster, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    image_url = models.CharField(max_length=500, blank=True)
    size_name = models.CharField(max_length=80)
    frame_name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.title} in Order {self.order.order_number}"
