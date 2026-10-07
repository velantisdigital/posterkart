from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/', views.add_to_cart_view, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item_quantity_view, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart_view, name='remove_cart_item'),
    path('coupon/apply/', views.apply_coupon_view, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon_view, name='remove_coupon'),
    path('drawer-json/', views.get_cart_drawer_json_view, name='drawer_json'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:poster_id>/', views.toggle_wishlist_api, name='toggle_wishlist'),
    path('wishlist/move-to-cart/<int:poster_id>/', views.move_wishlist_to_cart_view, name='move_to_cart'),
]
