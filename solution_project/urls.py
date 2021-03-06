from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt import views as jwt_views
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('service.api_v1_urls')),
    path('api/doc/', include('service.swagger_urls')),
    path('api-auth/', include('rest_framework.urls')),  # Add login/logout button in to the browsable API

    # path('api/v1/rest-auth/', include('rest_auth.urls')),  # Token API login/out, pass reset, pass change etc.

    # JWT
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),


]
