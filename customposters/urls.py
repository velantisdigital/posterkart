from django.urls import path
from . import views

app_name = 'customposters'

urlpatterns = [
    path('', views.create_custom_poster_view, name='create'),
]
