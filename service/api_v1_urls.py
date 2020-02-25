from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('users/', include('apps.c_users.urls')),
    path('vendors/', include('apps.vendors.urls')),
]
