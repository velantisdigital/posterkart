from django.contrib import admin
from .models import Category, PosterSize, FrameOption, Poster, PosterImage, Review


class PosterImageInline(admin.TabularInline):
    model = PosterImage
    extra = 2


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'poster_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(PosterSize)
class PosterSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'extra_price', 'dimensions', 'is_default', 'is_active', 'sort_order')
    list_editable = ('extra_price', 'is_default', 'is_active', 'sort_order')


@admin.register(FrameOption)
class FrameOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'frame_type', 'extra_price', 'color_code', 'is_default', 'is_active', 'sort_order')
    list_editable = ('extra_price', 'is_default', 'is_active', 'sort_order')


@admin.register(Poster)
class PosterAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'base_price', 'stock', 'rating', 'is_featured', 'is_trending', 'is_bestseller', 'created_at')
    list_filter = ('category', 'is_featured', 'is_trending', 'is_bestseller', 'created_at')
    list_editable = ('base_price', 'stock', 'is_featured', 'is_trending', 'is_bestseller')
    search_fields = ('title', 'description', 'tags', 'source_filename')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('source_filename',)
    inlines = [PosterImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('poster', 'user', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('poster__title', 'user__username', 'review_text')
