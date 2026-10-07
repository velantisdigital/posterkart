from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .forms import RegistrationForm, LoginForm, UserProfileForm, AddressForm
from .models import Address
from cart.utils import get_or_create_cart


def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Merge guest cart into newly registered user
            get_or_create_cart(request)
            login(request, user)
            messages.success(request, f"Welcome to PosterKart, {user.first_name or user.username}! Your account has been created.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('store:home')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'store:home'

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # Support login via email or username
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(request, username=username_or_email, password=password)

            if user is not None:
                login(request, user)
                # Seamlessly merge any session cart into user account
                get_or_create_cart(request)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username/email or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been safely logged out. See you soon!")
    return redirect('store:home')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been successfully updated.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)

    addresses = Address.objects.filter(user=user)
    recent_orders = user.orders.all()[:5]

    context = {
        'form': form,
        'addresses': addresses,
        'recent_orders': recent_orders,
        'total_orders': user.orders.count(),
        'wishlist_count': user.wishlist_items.count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def address_list_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses.html', {'addresses': addresses})


@login_required
def add_address_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'accounts:addresses'
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Address added successfully',
                    'address_id': address.id,
                    'formatted': address.formatted_address
                })
            messages.success(request, "New delivery address added successfully.")
            return redirect(next_url)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            messages.error(request, "Please check the address details for errors.")
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add New Address', 'next': next_url})


@login_required
def edit_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    next_url = request.GET.get('next') or request.POST.get('next') or 'accounts:addresses'

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery address updated.")
            return redirect(next_url)
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Address', 'next': next_url})


@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address deleted successfully.")
    return redirect('accounts:addresses')


@login_required
def set_default_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"'{address.full_name}' address set as default delivery address.")
    return redirect('accounts:addresses')
