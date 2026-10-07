from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from decimal import Decimal
from django.contrib.auth.models import User

from .models import Category, Poster, PosterSize, FrameOption, PosterImage, Review
from .forms import ReviewForm, ContactForm
from orders.models import Order
from customposters.models import CustomPoster


def home_view(request):
    featured_posters = Poster.objects.filter(is_active=True, is_featured=True).select_related('category')[:4]
    trending_posters = Poster.objects.filter(is_active=True, is_trending=True).select_related('category')[:4]
    new_arrivals = Poster.objects.filter(is_active=True).order_by('-created_at').select_related('category')[:4]
    bestseller_posters = Poster.objects.filter(is_active=True, is_bestseller=True).select_related('category')[:4]
    hero_poster = trending_posters.first() or featured_posters.first() or Poster.objects.filter(is_active=True).first()

    categories = Category.objects.filter(is_active=True).prefetch_related('posters')
    recent_reviews = Review.objects.select_related('user', 'poster').order_by('-created_at')[:6]

    context = {
        'featured_posters': featured_posters,
        'trending_posters': trending_posters,
        'new_arrivals': new_arrivals,
        'bestseller_posters': bestseller_posters,
        'hero_poster': hero_poster,
        'categories': categories,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'store/home.html', context)


def shop_view(request):
    posters = Poster.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.filter(is_active=True)

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        posters = posters.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q) |
            Q(tags__icontains=q)
        )

    # Category filter (single or multi)
    category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        posters = posters.filter(category=selected_category)

    # Price range filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            posters = posters.filter(base_price__gte=Decimal(min_price))
        except Exception:
            pass
    if max_price:
        try:
            posters = posters.filter(base_price__lte=Decimal(max_price))
        except Exception:
            pass

    # In-stock filter
    in_stock = request.GET.get('in_stock')
    if in_stock == '1':
        posters = posters.filter(stock__gt=0)

    # Sorting
    sort_by = request.GET.get('sort', 'popular')
    if sort_by == 'price_low':
        posters = posters.order_by('base_price')
    elif sort_by == 'price_high':
        posters = posters.order_by('-base_price')
    elif sort_by == 'newest':
        posters = posters.order_by('-created_at')
    elif sort_by == 'rating':
        posters = posters.order_by('-rating', '-created_at')
    else:  # 'popular'
        posters = posters.order_by('-is_trending', '-is_featured', '-rating', '-created_at')

    # Pagination: 12 posters per page
    paginator = Paginator(posters, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'posters': page_obj.object_list,
        'total_count': paginator.count,
        'categories': categories,
        'selected_category': selected_category,
        'current_q': q,
        'current_sort': sort_by,
        'current_min_price': min_price,
        'current_max_price': max_price,
    }
    return render(request, 'store/shop.html', context)


def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Strict validation: ONLY valid products belonging strictly to this category
    posters = Poster.objects.filter(
        category=category,
        is_active=True,
        main_image__isnull=False
    ).exclude(main_image='').exclude(title='')
    
    # Verify image files exist on disk to guarantee zero broken cards
    valid_ids = [p.id for p in posters if p.has_valid_image]
    posters = posters.filter(id__in=valid_ids)

    sort_by = request.GET.get('sort', 'popular')
    if sort_by == 'price_low':
        posters = posters.order_by('base_price')
    elif sort_by == 'price_high':
        posters = posters.order_by('-base_price')
    elif sort_by == 'newest':
        posters = posters.order_by('-created_at')
    elif sort_by == 'rating':
        posters = posters.order_by('-rating', '-created_at')
    else:
        posters = posters.order_by('-is_trending', '-is_featured', '-rating', '-created_at')

    paginator = Paginator(posters, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'posters': page_obj.object_list,
        'total_count': paginator.count,
        'current_sort': sort_by,
    }
    return render(request, 'store/category_detail.html', context)


def product_detail_view(request, slug):
    poster = get_object_or_404(Poster.objects.select_related('category').prefetch_related('gallery_images', 'reviews__user'), slug=slug)
    sizes = PosterSize.objects.filter(is_active=True).order_by('sort_order', 'extra_price')
    frames = FrameOption.objects.filter(is_active=True).order_by('sort_order', 'extra_price')
    related_posters = Poster.objects.filter(category=poster.category).exclude(id=poster.id)[:4]
    
    # Review form
    review_form = ReviewForm()
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(poster=poster, user=request.user).exists()

    context = {
        'poster': poster,
        'sizes': sizes,
        'frames': frames,
        'related_posters': related_posters,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'store/product_detail.html', context)


@require_GET
def quick_view_api(request, slug):
    try:
        poster = Poster.objects.select_related('category').prefetch_related('gallery_images').get(slug=slug)
        sizes = PosterSize.objects.filter(is_active=True).order_by('sort_order', 'extra_price')
        frames = FrameOption.objects.filter(is_active=True).order_by('sort_order', 'extra_price')

        data = {
            'id': poster.id,
            'slug': poster.slug,
            'title': poster.title,
            'category': poster.category.name,
            'description': poster.description[:220] + '...' if len(poster.description) > 220 else poster.description,
            'base_price': float(poster.base_price),
            'rating': float(poster.average_rating),
            'review_count': poster.review_count,
            'stock': poster.stock,
            'main_image': poster.main_image.url if poster.main_image else '/static/images/placeholder-poster.svg',
            'detail_url': poster.get_absolute_url(),
            'sizes': [{'id': s.id, 'name': s.name, 'code': s.code, 'extra_price': float(s.extra_price), 'is_default': s.is_default} for s in sizes],
            'frames': [{'id': f.id, 'name': f.name, 'frame_type': f.frame_type, 'extra_price': float(f.extra_price), 'color_code': f.color_code, 'is_default': f.is_default} for f in frames],
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Poster.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Poster not found'}, status=404)


@require_GET
def search_suggestions_api(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'suggestions': []})

    posters = Poster.objects.filter(
        is_active=True
    ).filter(
        Q(title__icontains=q) |
        Q(category__name__icontains=q) |
        Q(tags__icontains=q)
    ).select_related('category')[:6]

    suggestions = []
    for p in posters:
        suggestions.append({
            'title': p.title,
            'category': p.category.name,
            'price': float(p.base_price),
            'image': p.main_image.url if p.main_image else '/static/images/placeholder-poster.svg',
            'url': p.get_absolute_url(),
        })

    return JsonResponse({'suggestions': suggestions})


@login_required
@require_POST
def add_review_view(request, slug):
    poster = get_object_or_404(Poster, slug=slug)
    form = ReviewForm(request.POST)

    if form.is_valid():
        existing_review = Review.objects.filter(poster=poster, user=request.user).first()
        if existing_review:
            existing_review.rating = form.cleaned_data['rating']
            existing_review.review_text = form.cleaned_data['review_text']
            existing_review.save()
            messages.success(request, "Your review has been updated.")
        else:
            review = form.save(commit=False)
            review.poster = poster
            review.user = request.user
            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
    else:
        messages.error(request, "Unable to post review. Please check rating and comments.")

    return redirect('store:product_detail', slug=slug)


# Static / Informational Views
def about_view(request):
    return render(request, 'store/about.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Thank you for reaching out! Our team will get back to you within 24 hours.")
            return redirect('store:contact')
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'form': form})


def privacy_policy_view(request):
    return render(request, 'store/privacy_policy.html')


def terms_conditions_view(request):
    return render(request, 'store/terms_conditions.html')


def shipping_policy_view(request):
    return render(request, 'store/shipping_policy.html')


def return_policy_view(request):
    return render(request, 'store/return_policy.html')


# Custom Admin Dashboard
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='accounts:login')
def admin_dashboard_view(request):
    total_customers = User.objects.filter(is_staff=False).count()
    total_posters = Poster.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(payment_status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    pending_orders = Order.objects.filter(order_status__in=['PLACED', 'CONFIRMED', 'PRINTING']).count()
    delivered_orders = Order.objects.filter(order_status='DELIVERED').count()
    custom_requests_count = CustomPoster.objects.count()

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    recent_custom_posters = CustomPoster.objects.select_related('user', 'size', 'frame').order_by('-created_at')[:8]

    context = {
        'total_customers': total_customers,
        'total_posters': total_posters,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'custom_requests_count': custom_requests_count,
        'recent_orders': recent_orders,
        'recent_custom_posters': recent_custom_posters,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='accounts:login')
@require_POST
def admin_update_order_status_api(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('status')
    payment_status = request.POST.get('payment_status')

    if new_status in dict(Order.ORDER_STATUS_CHOICES):
        order.order_status = new_status
        if new_status == 'DELIVERED' and order.payment_method == 'COD':
            order.payment_status = 'PAID'
    
    if payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
        order.payment_status = payment_status

    order.save()
    messages.success(request, f"Order {order.order_number} updated to {order.get_order_status_display()}.")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'order_status': order.order_status,
            'order_status_display': order.get_order_status_display(),
            'payment_status': order.payment_status,
        })
    return redirect('store:admin_dashboard')
