from django.urls import path
from apps.c_users.views import UserView


urlpatterns = [
    path('', UserView.as_view(), name='custom_users'),
]