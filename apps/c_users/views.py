from rest_framework import generics

from .models import CustomUser
from .serializers import UserSerializer


class UserView(generics.ListAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

