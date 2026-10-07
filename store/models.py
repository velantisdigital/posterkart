import os
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, default='bi-tags', help_text="Bootstrap Icon class, e.g. bi-film")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'slug': self.slug})

    @property
    def valid_posters(self):
        return self.posters.filter(
            is_active=True,
            main_image__isnull=False
        ).exclude(main_image='').exclude(title='')

    @property
    def poster_count(self):
        return self.valid_posters.count()

    @property
    def cover_poster(self):
        """Find the best valid active poster to represent this category."""
        valid = self.valid_posters
        if not valid.exists():
            return None
        # Prefer real posters (with source_filename)
        real = valid.exclude(source_filename='')
        pool = real if real.exists() else valid
        # Prefer featured poster
        featured = pool.filter(is_featured=True).first()
        if featured and featured.has_valid_image:
            return featured
        # Then trending poster
        trending = pool.filter(is_trending=True).first()
        if trending and trending.has_valid_image:
            return trending
        # Otherwise first with valid image
        for p in pool:
            if p.has_valid_image:
                return p
        return None

    @property
    def cover_image(self):
        """Return the URL of the cover poster's image, or None if no valid poster exists."""
        poster = self.cover_poster
        if poster and poster.main_image:
            return poster.main_image.url
        return None


class PosterSize(models.Model):
    name = models.CharField(max_length=50, help_text="e.g. A4 (8.3 x 11.7 in)")
    code = models.CharField(max_length=10, unique=True, help_text="e.g. A4, A3, A2")
    extra_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Extra cost for this size")
    dimensions = models.CharField(max_length=50, blank=True, help_text="e.g. 21.0 x 29.7 cm")
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'extra_price']

    def __str__(self):
        if self.extra_price > 0:
            return f"{self.name} (+₹{self.extra_price:.0f})"
        return f"{self.name} (Base Price)"


class FrameOption(models.Model):
    FRAME_TYPES = (
        ('none', 'No Frame / Rolled Canvas'),
        ('black', 'Matte Black Wooden Frame'),
        ('white', 'Minimalist White Frame'),
        ('wooden', 'Natural Walnut Wooden Frame'),
    )

    name = models.CharField(max_length=100)
    frame_type = models.CharField(max_length=20, choices=FRAME_TYPES, default='none')
    extra_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    color_code = models.CharField(max_length=20, default='#1E1E1E', help_text="Hex color code for frame border preview")
    image = models.ImageField(upload_to='frames/', blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'extra_price']

    def __str__(self):
        if self.extra_price > 0:
            return f"{self.name} (+₹{self.extra_price:.0f})"
        return f"{self.name} (Free)"


class Poster(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posters')
    main_image = models.ImageField(upload_to='posters/')
    base_price = models.DecimalField(max_digits=8, decimal_places=2, default=299.00)
    stock = models.PositiveIntegerField(default=100)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for search")
    source_filename = models.CharField(max_length=255, blank=True, default='', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Poster.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    def calculate_price(self, size=None, frame=None):
        total = self.base_price
        if size:
            total += size.extra_price
        if frame:
            total += frame.extra_price
        return total

    @property
    def has_valid_image(self):
        if not self.main_image:
            return False
        try:
            return bool(self.main_image.name and self.main_image.url)
        except Exception:
            return False

    @property
    def is_valid_product(self):
        return bool(
            self.is_active and
            self.title and
            self.title.strip() and
            self.base_price and
            self.base_price > 0 and
            self.category_id and
            self.has_valid_image
        )

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg:
            return round(avg, 1)
        return float(self.rating)

    @property
    def review_count(self):
        return self.reviews.count()


class PosterImage(models.Model):
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='posters/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.poster.title}"


class Review(models.Model):
    RATING_CHOICES = (
        (5, '★★★★★ - Excellent'),
        (4, '★★★★☆ - Very Good'),
        (3, '★★★☆☆ - Good'),
        (2, '★★☆☆☆ - Fair'),
        (1, '★☆☆☆☆ - Poor'),
    )

    poster = models.ForeignKey(Poster, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poster_reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    review_text = models.TextField()
    is_verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.poster.title} ({self.rating}★)"
