from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=255, verbose_name="House/Flat/Block, Street")
    address_line_2 = models.CharField(max_length=255, blank=True, verbose_name="Area/Colony/Sector")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10, verbose_name="PIN Code")
    landmark = models.CharField(max_length=150, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.pin_code}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses for this user to is_default = False
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        elif not Address.objects.filter(user=self.user).exclude(pk=self.pk).exists():
            # If this is the only address, make it default automatically
            self.is_default = True
        super().save(*args, **kwargs)

    @property
    def formatted_address(self):
        lines = [self.address_line_1]
        if self.address_line_2:
            lines.append(self.address_line_2)
        if self.landmark:
            lines.append(f"Near {self.landmark}")
        lines.append(f"{self.city}, {self.state} - {self.pin_code}")
        lines.append(f"Phone: {self.phone_number}")
        return ", ".join(lines)
