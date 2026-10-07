from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<str:order_number>/', views.demo_payment_view, name='demo_payment'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('detail/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('tracking/<str:order_number>/', views.order_tracking_view, name='order_tracking'),
    path('cancel/<str:order_number>/', views.cancel_order_view, name='cancel_order'),
]
