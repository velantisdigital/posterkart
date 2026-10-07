from django.db import models
from django.contrib.auth.models import User
from store.models import PosterSize, FrameOption
from decimal import Decimal


class CustomPoster(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_posters', null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    uploaded_image = models.ImageField(upload_to='custom_posters/')
    size = models.ForeignKey(PosterSize, on_delete=models.SET_NULL, null=True)
    frame = models.ForeignKey(FrameOption, on_delete=models.SET_NULL, null=True)
    custom_text = models.CharField(max_length=255, blank=True, help_text="Optional custom quote or title on poster")
    special_instructions = models.TextField(blank=True, help_text="Any cropping or styling preferences")
    quantity = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('349.00'))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('349.00'))
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('349.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.username if self.user else "Guest"
        return f"Custom Poster #{self.id} by {user_str} ({self.created_at.strftime('%d %b %Y')})"

    def calculate_prices(self):
        unit = Decimal(str(self.base_price))
        if self.size:
            unit += Decimal(str(self.size.extra_price))
        if self.frame:
            unit += Decimal(str(self.frame.extra_price))
        self.unit_price = unit
        self.total_price = unit * Decimal(self.quantity)
        return self.unit_price, self.total_price

    def save(self, *args, **kwargs):
        self.calculate_prices()
        super().save(*args, **kwargs)
