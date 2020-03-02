

from .models import CustomUser
from .serializers import UserSerializer

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from .serializers import RefreshTokenSerializer


class UserView(ListAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class LogoutView(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        """Needed"""
        return

    def post(self, request, *args):
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response(status=status.HTTP_204_NO_CONTENT)