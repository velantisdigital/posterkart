from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from store.models import Poster, PosterSize, FrameOption
from customposters.models import CustomPoster
from django.conf import settings


class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('PERCENT', 'Percentage Discount (%)'),
        ('FIXED', 'Flat Amount Discount (₹)'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='PERCENT')
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, help_text="e.g. 10 for 10% or 100 for ₹100")
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    max_discount_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Cap for percentage discounts")
    active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=1000)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'PERCENT' else '₹'} OFF)"

    def is_valid(self, subtotal):
        if not self.active:
            return False, "This coupon is currently inactive."
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False, "This coupon has expired."
        if self.used_count >= self.usage_limit:
            return False, "This coupon usage limit has been reached."
        if Decimal(str(subtotal)) < self.min_order_amount:
            return False, f"Minimum order amount of ₹{self.min_order_amount:.0f} required to use this coupon."
        return True, "Coupon is valid."

    def calculate_discount(self, subtotal):
        subtotal = Decimal(str(subtotal))
        valid, msg = self.is_valid(subtotal)
        if not valid:
            return Decimal('0.00')

        if self.discount_type == 'PERCENT':
            discount = (subtotal * Decimal(str(self.discount_value))) / Decimal('100')
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = Decimal(str(self.max_discount_amount))
            return discount.quantize(Decimal('0.01'))
        else:
            return min(Decimal(str(self.discount_value)), subtotal).quantize(Decimal('0.01'))


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart session {self.session_key}"

    def get_subtotal(self):
        return sum(item.total_price for item in self.items.all())

    def get_delivery_charge(self):
        subtotal = self.get_subtotal()
        if subtotal == 0:
            return Decimal('0.00')
        free_thresh = getattr(settings, 'FREE_DELIVERY_THRESHOLD', 499.00)
        std_charge = getattr(settings, 'STANDARD_DELIVERY_CHARGE', 50.00)
        if subtotal >= Decimal(str(free_thresh)):
            return Decimal('0.00')
        return Decimal(str(std_charge))

    def get_discount_amount(self):
        if self.coupon:
            return self.coupon.calculate_discount(self.get_subtotal())
        return Decimal('0.00')

    def get_total(self):
        subtotal = self.get_subtotal()
        if subtotal == 0:
            return Decimal('0.00')
        delivery = self.get_delivery_charge()
        discount = self.get_discount_amount()
        total = subtotal + delivery - discount
        return max(total, Decimal('0.00')).quantize(Decimal('0.01'))

    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE, null=True, blank=True)
    custom_poster = models.ForeignKey(CustomPoster, on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(PosterSize, on_delete=models.CASCADE)
    frame = models.ForeignKey(FrameOption, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def calculate_prices(self):
        if self.poster:
            base = Decimal(str(self.poster.base_price))
        elif self.custom_poster:
            base = Decimal(str(self.custom_poster.base_price))
        else:
            base = Decimal('299.00')

        size_extra = Decimal(str(self.size.extra_price)) if self.size else Decimal('0.00')
        frame_extra = Decimal(str(self.frame.extra_price)) if self.frame else Decimal('0.00')

        unit = base + size_extra + frame_extra
        self.unit_price = unit
        self.total_price = unit * Decimal(self.quantity)
        return self.unit_price, self.total_price

    def save(self, *args, **kwargs):
        self.calculate_prices()
        super().save(*args, **kwargs)

    @property
    def title(self):
        if self.poster:
            return self.poster.title
        elif self.custom_poster:
            return f"Custom Poster ({self.custom_poster.custom_text or 'Personalized'})"
        return "Poster Item"

    @property
    def image_url(self):
        if self.poster and self.poster.main_image:
            return self.poster.main_image.url
        elif self.custom_poster and self.custom_poster.uploaded_image:
            return self.custom_poster.uploaded_image.url
        return "/static/images/placeholder-poster.svg"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poster')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.poster.title}"
