from django.urls import path
from apps.c_users.views import UserView, LogoutView


urlpatterns = [
    path('', UserView.as_view(), name='custom_users'),
    path('user_logout/', LogoutView.as_view()),
]