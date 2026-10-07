from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('shop/', views.shop_view, name='shop'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('poster/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('poster/<slug:slug>/review/', views.add_review_view, name='add_review'),

    # APIs for Interactive Micro-interactions
    path('api/quick-view/<slug:slug>/', views.quick_view_api, name='quick_view_api'),
    path('api/search-suggestions/', views.search_suggestions_api, name='search_suggestions_api'),

    # Informational Pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('shipping-policy/', views.shipping_policy_view, name='shipping_policy'),
    path('return-policy/', views.return_policy_view, name='return_policy'),

    # Custom Staff Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/orders/<str:order_number>/update-status/', views.admin_update_order_status_api, name='admin_update_order_status'),
]
